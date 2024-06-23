from dotenv import load_dotenv,dotenv_values
import json
import os
from sentence_transformers import SentenceTransformer

from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient, SearchIndexingBufferedSender  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryCaptionResult,
    QueryAnswerResult,
    SemanticErrorMode,
    SemanticErrorReason,
    SemanticSearchResultsType,
    QueryType,
    VectorizedQuery,
    VectorQuery,
    VectorFilterMode,    
)
from azure.search.documents.indexes.models import (  
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticPrioritizedFields,
    SemanticField,  
    SearchField,  
    SemanticSearch,
    VectorSearch,  
    HnswAlgorithmConfiguration,
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticField,  
    SearchField,  
    VectorSearch,  
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)  


class CustomAzureSearch:
    def __init__(self,
                 endpoint,
                 key,
                 index_name,
                 number_results_to_return,
                 number_near_neighbors,
                 model_name = None,
                 embedding_field_name = None,
                 semantic_config = None):
        self.endpoint = endpoint
        self.key = key
        self.index_name = index_name
        self.model_name = model_name
        self.embedding_field_name = embedding_field_name
        self.number_results_to_return = number_results_to_return
        self.number_near_neighbors = number_near_neighbors
        self.semantic_config = semantic_config
        self.client = SearchClient(
                endpoint=self.endpoint, 
                index_name=self.index_name,
                credential=AzureKeyCredential(self.key))
        
    def upload_documents(self,documents):
        """Uploads documents to the index
        """
        if self.client:
            self.client.upload_documents(documents=documents)
        else:
            print("Client not initialized")
            self.client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.key))
            self.client.upload_documents(documents=documents)
    
    
        
    def create_index(self):
        """Creates the index
        """
        credential = AzureKeyCredential(self.key)

        search_index_client = SearchIndexClient(endpoint=self.endpoint, 
                                                credential=credential)
        
        fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, 
                key=True, sortable=True, 
                filterable=True, facetable=True),
    SearchableField(name="sourcefile", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
    SearchableField(name="sourcepage", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
    SearchableField(name="category", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
    SearchableField(name="content", type=SearchFieldDataType.String,
                    searchable = True),
    SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=384, 
                vector_search_profile_name="BOBHnswProfile")
]

        # Configure the vector search configuration  
        vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="BOBHnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="BOBExhaustiveKnn",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="BOBHnswProfile",
                algorithm_configuration_name="BOBHnsw",
            ),
            VectorSearchProfile(
                name="BOBExhaustiveKnnProfile",
                algorithm_configuration_name="BOBExhaustiveKnn",
            )
        ]
    )

        semantic_config = SemanticConfiguration(
    name=self.semantic_config, # The name of the semantic configuration
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        keywords_fields=[SemanticField(field_name="sourcefile")]
    )
)
    
    # Create the semantic settings with the configuration
        semantic_search = SemanticSearch(configurations=[semantic_config])

  
    # Create the search index with the semantic settings
        search_index = SearchIndex(name=self.index_name, fields=fields,
                    vector_search=vector_search, 
                    semantic_search=semantic_search)
        result = search_index_client.create_or_update_index(search_index)
        print("Create Index Result: ", result)


    
    def get_results_vector_search(self,query,
                                  list_fields=None):
        
        """
        [summary]
        This returns the results of a vector search
        query: string
        list_fields: list of fields to return
        """
        
        vector_query = self.get_vectorized_query(query)
        
        results = self.client.search(  
            search_text=None,  
            vector_queries=[vector_query],
            select=list_fields,
            top=self.number_results_to_return,
        )  
        
        return self.__get_results_to_return(results)

    def get_vectorized_query(self, query,exhaustive_knn=False):

        """This returns a vectorized query

        Caters for both exhaustive knn queries and regular queries

        Steps:
            1. Gets the query as the input
            2. Gets the vector of the query using the model
            3. Returns the vectorized query
            3.1. If exhaustive_knn is True, then it returns an exhaustive knn query
            3.2. If exhaustive_knn is False, then it returns a regular knn query
        """
        query_vector = self.get_embedding_query_vector(query)

        if exhaustive_knn:
            vector_query = VectorizedQuery(vector=query_vector, 
                               k_nearest_neighbors=self.number_near_neighbors, 
                               fields=self.embedding_field_name,
                               exhaustive_knn =True)
        else:
            vector_query = VectorizedQuery(vector=query_vector, 
                               k_nearest_neighbors=self.number_near_neighbors, 
                               fields=self.embedding_field_name)
                               
        return vector_query

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

    def __get_results_to_return(self, results):

        """This returns the results to return
        """
        results_to_return = []
        metadata_source_filename_to_return = []
        metadata_source_page_to_return = []
        reranker_score_to_return = []
        for result in results:
            results_to_return.append(result['content'])

            if '@search.reranker_score' in result:
                reranker_score_to_return.append(result['@search.reranker_score'])
            
            metadata_source_page_to_return.append(result['sourcepage'])
            metadata_source_filename_to_return.append(result['sourcefile'])
        return results_to_return, \
                metadata_source_filename_to_return, \
                metadata_source_page_to_return, reranker_score_to_return
    
    def get_results_hybrid_search(self,query,
                                  list_fields=None):
        
        """This returns the results of a hybrid search
        which is a combination of a vector search and a regular search

        Returns:
            Results of the query
        """
        
        vector_query = self.get_vectorized_query(query)
        
        
        results = self.client.search(  
            search_text=query,  
            vector_queries=[vector_query],
            select=list_fields,
            top=self.number_results_to_return,
        )  
        
        return self.__get_results_to_return(results)
    
    def get_results_exhaustive_knn(self,query,
                                  list_fields=None):
        
        """Provides the results of an exhaustive knn query

        Returns:
            [list,list]: results of the query
        """
        
        vector_query = self.get_vectorized_query(query,
                                                 exhaustive_knn=True)
        
        
        results = self.client.search(  
            search_text=query,  
            vector_queries=[vector_query],
            select=list_fields,
            top=self.number_results_to_return,
        )  
        
        return self.__get_results_to_return(results)
    
    def get_results_semantic_search(self,query,
                                    list_fields=None):
            
            """Provides the results of a semantic search query
    
            Returns:
                _type_: results of the query
            """
            
            vector_query = self.get_vectorized_query(query)
            
            results = self.client.search(  
                    search_text=query,  
                    vector_queries=[vector_query],
                    select=list_fields,
                    query_type=QueryType.SEMANTIC, 
                    semantic_configuration_name=self.semantic_config, 
                    query_caption=QueryCaptionType.EXTRACTIVE, 
                    query_answer=QueryAnswerType.EXTRACTIVE,
                    top=self.number_results_to_return,
                )  
            
            return self.__get_results_to_return(results)