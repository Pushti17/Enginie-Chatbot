# Enginie-Chatbot
Enginie is RAG(Retrieval Augmented Generation) based chatbot made 
specifically for college SSEC. it will provide various information about 
college's department, facilities, rules, faculties etc. It is user friendly chatbot 
which will do conversation with user in their own humanoid Natural 
language by text as well as speech.

Main Functionality 
• Fast data Access : Fetching the websites data just by adding the query without finding it on different webpages.  
• Easy data access : User convenience and natural language interaction and summarized answer. 

Tech-Stack 

❖ Frontend 
• HTML 
• CSS 
• JavaScript 

❖ Backend 
➢ Local LLM (Ollama) - Mistral-7b-instruct 
  It is a 7.3-billion-parameter foundational language model released by 
  Mistral AI.  Designed for high efficiency, low latency, and superior 
  performance compared to larger models. 
➢ Python Libraries 
o For Crawling and Data scraping 
  ▪ Selenium 
  ▪ BeutifulSoup 
  ▪ Asyncio & Aiohttp  
o For Chunking and embedding 
  ▪ Numpy 
  ▪ Faiss 
  ▪ Sentence_transformers 
o For Query analysis and answering (Main function) 
  ▪ Flask 
  ▪ Langchain_ollama 
❖ Database 
  • JSON  

WorkFlow(Execute these files in order)

Crawler -> Extract -> indexing -> app
