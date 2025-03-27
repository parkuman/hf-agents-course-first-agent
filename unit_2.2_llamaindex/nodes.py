from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

reader = SimpleDirectoryReader(input_dir="./files")
documents = reader.load_data()

parser = SentenceSplitter()
nodes = parser.get_nodes_from_documents(documents)
