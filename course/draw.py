"""Runnable(LCEL 체인, LangGraph 그래프)의 구조를 노트북에 그림으로 보여 준다.

    from draw import draw
    draw(chain)        # LCEL 체인
    draw(app)          # LangGraph compile() 결과

그림은 get_graph().draw_png()가 내 PC 안에서 그린다(pygraphviz). Mermaid(mermaid.ink)처럼
외부 사이트에 접속하지 않으므로 사내망에서도 된다. 그림을 못 만들면 글자 그림을 대신 보여 준다.
"""

from IPython.display import Image, display


def draw(runnable, xray: bool = False):
    """runnable.get_graph()를 PNG로 그린다. 실패하면 글자 그림(draw_ascii)을 보여 준다."""
    graph = runnable.get_graph(xray=xray) if xray else runnable.get_graph()
    # Parallel<length>Input 같은 노드 이름의 <, >가 그림 글자(HTML) 태그로 읽히지 않게 바꾼다
    names = {n.id: n.name.replace("<", "&lt;").replace(">", "&gt;") for n in graph.nodes.values()}
    try:
        display(Image(graph.draw_png(labels={"nodes": names, "edges": {}})))
    except Exception as exc:  # pygraphviz 미설치 등
        print(f"그림을 만들지 못해 글자 그림으로 보여 줍니다 ({type(exc).__name__}: {exc}).")
        print(graph.draw_ascii())
