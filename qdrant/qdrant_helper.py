import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *
from sentence_transformers import SentenceTransformer


class QdrantHelper:
    def __init__(self,
                 URL,
                 API_KEY,
                 MODEL_NAME,
                 COLLECTION_NAME,
                 METRIC=qmodels.Distance.COSINE,
                 DIMENSION = 384,
                 ):
        self.client = qc.QdrantClient(url=URL,api_key=API_KEY)
        self.metric = METRIC
        self.dimension = DIMENSION
        self.model_name = MODEL_NAME
        self.collection = COLLECTION_NAME
    
    def create_index(self,
                          COLLECTION_NAME,
                          ):
        self.collection = COLLECTION_NAME
        self.client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=self.dimension, 
                    distance=self.metric
                ),
            )
        
    def upload_documents(self,
                         id_list,
                         embeddings_all,
                         payload_list):
        
        embeddings_all_len = len(embeddings_all)

        CHUNK_SIZE = 100
        for i in range(0, embeddings_all_len, CHUNK_SIZE):
            if(i+CHUNK_SIZE > embeddings_all_len -1):
                new_chunk = embeddings_all_len -1
            else:
                new_chunk = i+CHUNK_SIZE -1
            print("Inserting chunk", i , "to", new_chunk)
            self.client.upsert(
                collection_name=self.collection,
                points=qmodels.Batch(
                    ids = id_list[i:new_chunk],
                    vectors=embeddings_all[i:new_chunk],
                    payloads=payload_list[i:new_chunk]
                ),
            )
    def get_embedding_query_vector(self, query):
        """Get the vector of the query

        Args:
            query (string): user input

        Returns:
            _type_: vector of the query
        """
        model = SentenceTransformer(self.model_name)
        query_vector = model.encode(query)
        return query_vector
    
    def get_search_results(self,user_input, CATEGORY=None):

        
        query_vector = self.get_embedding_query_vector(user_input)

        print(user_input)
        print("################################")
        print(query_vector)
        print("################################")
        if CATEGORY == '' or CATEGORY == None:
            query_filter = None
        else:
            query_filter=qmodels.Filter(
                must= [
                    FieldCondition(
                        key="Category",
                        match=models.MatchValue(value=CATEGORY),
                    )
                ],
            )
        search_result = self.client.search(collection_name=self.collection,
                                        query_vector=query_vector.tolist(), 
                                        query_filter=query_filter,
                                        limit=5)
       
        return (self.__get_results_to_return(search_result))
    
    def __get_results_to_return(self, results):

        """This returns the results to return
        """
        results_to_return = []
        metadata_source_filename_to_return = []
        metadata_source_page_to_return = []
        reranker_score_to_return = []
        for result in results:
            results_to_return.append(result.payload['content'])

            if '@search.reranker_score' in result.payload:
                reranker_score_to_return.append(result.payload['@search.reranker_score'])
            
            metadata_source_page_to_return.append(result.payload['sourcepage'])
            metadata_source_filename_to_return.append(result.payload['sourcefile'])

        return results_to_return, \
                metadata_source_filename_to_return, \
                metadata_source_page_to_return, reranker_score_to_return
    