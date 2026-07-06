from src.task_decomposer.decomposer import TaskDecomposer
d = TaskDecomposer()
tasks = d.decompose("Hello. Open NotePad. Explain Embeddings")
for t in tasks:
    print(f"[{t.order}] {t.text}")
