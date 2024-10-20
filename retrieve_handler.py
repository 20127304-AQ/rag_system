import re
import asyncio
import tornado
from base_handler import BaseHandler
from utils import search_code, get_db_and_table

# Handler for retrieval task
class RetrieveHandler(BaseHandler):
    async def post(self):
        user_id = self.current_user
        db, table_name = await get_db_and_table(user_id)
        
        data = tornado.escape.json_decode(self.request.body)
        query = data.get('query', '') or data.get('fullInput', '')
        
        # Truncate "My Custom Context" if found
        query = re.sub(r'^My Custom Context\s*', '', query, flags=re.IGNORECASE)
        
        print(f"Processed search query: {query}")
        
        if not query:
            print("No valid search terms found")
            self.write([])
            return

        try:
            results_df = await search_code(query, db, table_name)
            
            context_items = [
                {
                    "name": row["filename"],
                    "description": row["filename"],
                    "content": row["text"],
                }
                for _, row in results_df.iterrows()
            ]
            
            self.write({"context_items": context_items})
        except Exception as e:
            print(f"Error during search: {str(e)}")
            self.write({"status": "Error", "message": str(e)})