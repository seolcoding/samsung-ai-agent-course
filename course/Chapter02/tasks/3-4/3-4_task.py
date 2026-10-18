"""3-4 과제: 그래프 나누고 기억하기

실행(저장소 맨 위에서):
    uv run --env-file .env python course/Chapter02/tasks/3-4/3-4_task.py

할 일과 프롬프트 힌트는 같은 폴더의 README.md에 있습니다.
"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()

# 과제에 쓰는 값(그대로 둡니다)
DOCUMENT = (
    "인공지능은 인간의 지능을 모방하는 컴퓨터 시스템으로, 최근 LLM의 등장으로 급격히 발전했습니다. "
    "이제 AI는 텍스트 생성, 번역, 코딩 등 다양한 작업을 수행할 수 있습니다."
)
TOPIC = "재택근무"
USER_ID = "user_001"
USER_INFO = "이름은 이지수, 취미는 피아노 연주"


# ✍️ 목표 1: 서브그래프 summary_subgraph를 따로 compile하고, 부모 그래프 parent_graph의 노드에서 호출해 summary를 부모 State로 넘깁니다.
print("=== 목표 1: 서브그래프 ===")
print("(아직 작성하지 않았습니다)")


# ✍️ 목표 2: pros·cons 두 노드를 START에서 동시에 실행하고 merge로 모으는 fan_graph를 만듭니다. 결과는 Annotated 리듀서가 붙은 notes에 모읍니다.
print("\n=== 목표 2: fan-out/fan-in ===")
print("(아직 작성하지 않았습니다)")


# ✍️ 목표 3: MemorySaver를 붙인 chat_graph로 thread_a는 두 번, thread_b는 한 번 대화하고 get_state로 thread마다 메시지 수를 출력합니다.
print("\n=== 목표 3: MemorySaver와 thread_id ===")
print("(아직 작성하지 않았습니다)")


# ✍️ 목표 4: InMemoryStore에 USER_INFO를 put하고, 새 thread에서 search로 꺼내 쓰는 store_graph로 "내 이름이랑 취미 알아?"에 답하게 합니다.
print("\n=== 목표 4: InMemoryStore ===")
print("(아직 작성하지 않았습니다)")
