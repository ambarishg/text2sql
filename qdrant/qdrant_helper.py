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
                 RESULTS_LIMIT = 5
                 ):
        self.client = qc.QdrantClient(url=URL,api_key=API_KEY)
        self.metric = METRIC
        self.dimension = DIMENSION
        self.model_name = MODEL_NAME
        self.collection = COLLECTION_NAME
        self.results_limit = RESULTS_LIMIT
    
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
    
    def get_search_results(self, user_input, 
                           CATEGORY=None, 
                           user_id=None):
        # Generate the query vector from the user input
        query_vector = self.get_embedding_query_vector(user_input)

        print(user_input)
        print("################################")
        print(query_vector)
        print("################################")
        print(f"category = {CATEGORY}")
        print(f"user_id = {user_id}")
        
        # Initialize query_filter based on CATEGORY and user_id
        must_conditions = []
        
        # Add category condition if provided
        if CATEGORY and CATEGORY != '':
            must_conditions.append(
                FieldCondition(
                    key="category",
                    match=models.MatchValue(value=CATEGORY),
                )
            )
        
        # Add user_id condition if provided
        if user_id is not None:
            must_conditions.append(
                FieldCondition(
                    key="user_id",  # Assuming "UserId" is the field name in your database
                    match=models.MatchValue(value=user_id),
                )
            )
        
        # Create query filter only if there are conditions to apply
        query_filter = qmodels.Filter(must=must_conditions) if must_conditions else None
        
        # Perform the search with the constructed query vector and filter
        search_result = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector.tolist(), 
            query_filter=query_filter,
            limit=self.results_limit
        )
        
        return self.__get_results_to_return(search_result)

    def __get_results_to_return(self, results):

        """This returns the results to return
        """
        results_to_return = []
        metadata_source_filename_to_return = []
        metadata_source_page_to_return = []
        reranker_score_to_return = []

        if not results:
            print("No results found")
            
        for result in results:
            print(result.score)                
            results_to_return.append(result.payload['content'])

            if '@search.reranker_score' in result.payload:
                reranker_score_to_return.append(result.payload['@search.reranker_score'])
            
            metadata_source_page_to_return.append(result.payload['sourcepage'])
            metadata_source_filename_to_return.append(result.payload['sourcefile'])

        return results_to_return, \
                metadata_source_filename_to_return, \
                metadata_source_page_to_return, reranker_score_to_return
    