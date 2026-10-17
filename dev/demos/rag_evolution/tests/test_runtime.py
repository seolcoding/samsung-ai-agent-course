"""외부 API 없이 실제 그래프 분기·설정·근거·조회 실패를 검증한다."""
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, Mock

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from documents import load_pdf_documents, pdf_fingerprint
from graphs import build_basic_graph, build_advanced_graph, parse_review, MAX_TOOL_ROUNDS
from runtime_config import resolve_settings, initial_mode, cache_fingerprint, SamsungEmbeddings, client_options
from tools import make_tools


class FakeModel:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.inputs = []
    def invoke(self, messages):
        self.inputs.append(messages)
        return next(self.replies)


def call(name='cost_sum', args=None):
    return AIMessage(content='', tool_calls=[{'name':name,'args':args or {'amounts':[100,200]},'id':'call1','type':'tool_call'}])


def state():
    return {'messages':[HumanMessage(content='비용 합계를 구해 줘')], 'question':'비용 합계', 'system':'한국어',
            'llm_calls':0,'tool_rounds':0,'rewrites':0}


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.tools = {t.name:t for t in make_tools()}
    def test_basic_tool_loop_and_messages(self):
        model=FakeModel([call(),AIMessage(content='300원')])
        graph=build_basic_graph(model,self.tools)
        result=graph.invoke(state())
        self.assertEqual(result['visits'],['agent','tools','agent'])
        self.assertEqual(result['evidence'][0]['result']['total'],300)
        self.assertIsInstance(model.inputs[-1][-1],ToolMessage)
        self.assertEqual(result['llm_calls'],2)
    def test_basic_without_tools(self):
        result=build_basic_graph(FakeModel([AIMessage(content='안녕하세요')]),self.tools).invoke(state())
        self.assertEqual(result['visits'],['agent'])
    def test_loop_cap(self):
        result=build_basic_graph(FakeModel([call() for _ in range(MAX_TOOL_ROUNDS+1)]),self.tools).invoke(state(),{'recursion_limit':40})
        self.assertIn('error',result)
        self.assertEqual(result['tool_rounds'],MAX_TOOL_ROUNDS)
    def advanced(self,reviews):
        researcher=FakeModel([call(),AIMessage(content='입력 비용 근거')])
        writer=FakeModel([AIMessage(content=f'초안{i}') for i in range(3)])
        reviewer=FakeModel([AIMessage(content=x) for x in reviews])
        graph=build_advanced_graph(researcher,writer,reviewer,self.tools)
        return graph.invoke(state()),graph,writer,reviewer
    def test_review_pass(self):
        result,_,writer,reviewer=self.advanced(['{"passed":true,"feedback":"근거 일치"}'])
        self.assertEqual(result['review']['status'],'passed')
        self.assertEqual(result['rewrites'],0)
        self.assertIn('300',writer.inputs[0][-1].content)
        self.assertIn('300',reviewer.inputs[0][-1].content)
    def test_rewrite_then_pass(self):
        result,_,writer,_=self.advanced(['{"passed":false,"feedback":"출처 추가"}','{"passed":true,"feedback":"확인"}'])
        self.assertEqual(result['rewrites'],1)
        self.assertEqual(result['review']['status'],'passed')
        self.assertIn('출처 추가',writer.inputs[-1][-1].content)
    def test_rewrite_limit(self):
        result,_,writer,_=self.advanced(['{"passed":false,"feedback":"수정"}']*3)
        self.assertEqual(result['review']['status'],'limit')
        self.assertEqual(result['rewrites'],2)
        self.assertEqual(len(writer.inputs),3)
    def test_malformed_review_fails(self):
        for text in ('not json','{"passed":"true","feedback":"ok"}','[]','{"passed":true}'):
            with self.subTest(text=text):
                result,_,writer,_=self.advanced([text])
                self.assertEqual(result['review']['status'],'error')
                self.assertEqual(len(writer.inputs),1)
    def test_displayed_mermaid_matches_execution_factory(self):
        from backend import graph_mermaid
        self.assertEqual(graph_mermaid(5),build_basic_graph(None,{}).get_graph().draw_mermaid(with_styles=False))
        self.assertEqual(graph_mermaid(8),build_advanced_graph(None,None,None,{}).get_graph().draw_mermaid(with_styles=False))

    def test_mermaid_edges(self):
        basic=build_basic_graph(None,{})
        advanced=build_advanced_graph(None,None,None,{})
        edges={(e.source,e.target) for e in basic.get_graph().edges}
        self.assertIn(('agent','tools'),edges)
        self.assertIn(('tools','agent'),edges)
        edges={(e.source,e.target) for e in advanced.get_graph().edges}
        self.assertIn(('reviewer','writer'),edges)
        self.assertIn(('researcher_tools','researcher'),edges)


class SettingsTests(unittest.TestCase):
    def test_ui_mode_wins_and_environment_not_mutated(self):
        before=dict(os.environ)
        values={'LLM_PROVIDER':'samsung','EMBED_PROVIDER':'samsung','COURSE_ENV':'out','OPENAI_API_KEY':'fake','OPENAI_MODEL':'model-A'}
        settings=resolve_settings('OpenAI 실행',values.get)
        self.assertEqual(initial_mode(values.get),'samsung')
        self.assertEqual(settings['llm_provider'],'openai')
        self.assertEqual(settings['embed_provider'],'openai')
        self.assertEqual(settings['model'],'model-A')
        self.assertEqual(dict(os.environ),before)
    def test_cache_separation(self):
        settings=resolve_settings('openai',{'OPENAI_API_KEY':'fake','OPENAI_MODEL':'a'}.get)
        base=cache_fingerprint(settings,600)
        for key in ('OPENAI_API_KEY','OPENAI_MODEL','api_base_url','embedding_api_url','embedding_x_dep_ticket'):
            changed={**settings,key:'different'}
            self.assertNotEqual(base,cache_fingerprint(changed,600),key)
        self.assertNotEqual(base,cache_fingerprint(settings,300))
    def test_gateway_headers(self):
        settings=resolve_settings('samsung',{'api_base_url':'https://internal.invalid/v1','credential_key':'fake','send_system_name':'class','user_id':'user','model':'inside'}.get)
        options=client_options(settings)
        self.assertEqual(options['base_url'],'https://internal.invalid/v1')
        self.assertEqual(options['default_headers']['x-dep-ticket'],'fake')
        self.assertEqual(options['default_headers']['User-Type'],'AD_ID')
        self.assertNotEqual(options['default_headers']['Prompt-Msg-Id'],client_options(settings)['default_headers']['Prompt-Msg-Id'])
    def test_embedding_batches_and_order(self):
        calls=[]
        def post(url,**kwargs):
            calls.append((url,kwargs))
            data=[{'index':i,'embedding':[float(int(t))]} for i,t in enumerate(kwargs['json']['input'])]
            response=Mock(); response.json.return_value={'data':list(reversed(data))}
            return response
        settings={'embedding_api_url':'https://internal.invalid','embedding_x_dep_ticket':'fake'}
        with patch('runtime_config.requests.post',side_effect=post):
            result=SamsungEmbeddings(settings).embed_documents([str(i) for i in range(23)])
        self.assertEqual([len(x[1]['json']['input']) for x in calls],[10,10,3])
        self.assertEqual(result,[[float(i)] for i in range(23)])
        self.assertEqual(calls[0][1]['headers']['x-dep-ticket'],'fake')
        self.assertEqual(calls[0][0],'https://internal.invalid/v1/embeddings')


class DataToolsTests(unittest.TestCase):
    def setUp(self): self.tools={t.name:t for t in make_tools()}
    def test_pdf_hash_and_pages(self):
        manifest=json.loads((APP/'data/pdf_manifest.json').read_text(encoding='utf-8'))
        original=APP.parents[2]/manifest['source_path']
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),pdf_fingerprint())
        docs=load_pdf_documents()
        self.assertEqual(len(docs),28)
        self.assertEqual([d.metadata['page'] for d in docs],list(range(1,29)))
        self.assertTrue(all(d.page_content and d.metadata['year']==2024 for d in docs))
    def test_pdf_tool_only_without_search_index(self):
        self.assertIn('insurance_pdf_page',self.tools)
        self.assertNotIn('insurance_search',self.tools)
        self.assertFalse(self.tools['insurance_pdf_page'].invoke({'page':0})['ok'])
        result=self.tools['insurance_pdf_page'].invoke({'page':28})
        self.assertTrue(result['ok'])
        self.assertEqual(result['sources'][0]['page'],28)
        with_search={t.name for t in make_tools(lambda:None,3)}
        self.assertIn('insurance_search',with_search)
        self.assertNotIn('insurance_pdf_page',with_search)
    def test_decimal_sum_and_invalid(self):
        self.assertEqual(self.tools['cost_sum'].invoke({'amounts':[0.1,0.2]})['total'],0.3)
        for amounts in ([],[-1],[float('inf')]):
            self.assertFalse(self.tools['cost_sum'].invoke({'amounts':amounts})['ok'])
    def test_wiki_missing_and_timeout(self):
        with patch('tools._api',return_value={}):
            self.assertEqual(self.tools['wikipedia_search'].invoke({'query':'unknown'})['status'],'no_results')
        import requests
        with patch('tools.requests.get',side_effect=requests.Timeout('sensitive error')):
            result=self.tools['wikipedia_search'].invoke({'query':'cat'})
            self.assertEqual(result['status'],'timeout')
            self.assertNotIn('sensitive',str(result))
    def test_photo_missing(self):
        with patch('tools._api',return_value={}):
            self.assertFalse(self.tools['animal_photo'].invoke({'animal':'cat'})['ok'])
    def test_retrieval_empty_and_source_metadata(self):
        store=Mock(); store.similarity_search.return_value=[]
        search={t.name:t for t in make_tools(lambda:store,2)}['insurance_search']
        self.assertEqual(search.invoke({'query':'보장'})['status'],'no_results')
        store.similarity_search.return_value=[load_pdf_documents()[1]]
        result=search.invoke({'query':'보장'})
        self.assertEqual(result['sources'][0]['page'],2)
        store.similarity_search.assert_called_with('보장',k=2)


if __name__=='__main__': unittest.main()
