from ..data.dataloader import DataLoader
from .services.embedding import EmbeddingService
from .services.query import QueryService
if __name__ == '__main__':
    loader=DataLoader(file_path=r'D:\WORKSPACE\intern_task\backend\data\dataset',cache_file=r'D:\WORKSPACE\intern_task\backend\data\ocr_cache.pkl')
    data=loader.read_and_process()
    embedding=EmbeddingService()
    embedding.build_and_save_vectorstore(data)
    query=" what is modulation?"
    Q=QueryService().query(user_query=query)
    print(Q)
