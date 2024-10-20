import asyncio
import tornado
from base_handler import BaseHandler
from utils import remove_embeddings_for_folders, get_all_files_in_folder, index_code, get_db_and_table

# Handler for reindexing task
class ReindexHandler(BaseHandler):
    async def post(self):
        user_id = self.current_user
        db, table_name = await get_db_and_table(user_id)
        
        data = tornado.escape.json_decode(self.request.body)
        folder_paths = data.get('folder_paths', [])

        # Remove existing embeddings for the specified folders
        await remove_embeddings_for_folders(folder_paths, db, table_name)

        # Get all files from the specified folders
        files_to_index = []
        for folder_path in folder_paths:
            files_to_index.extend(get_all_files_in_folder(folder_path))

        if files_to_index:
            await index_code(files_to_index, db, table_name)
            self.write({"status": f"Re-indexing complete for {len(files_to_index)} files in the specified folders."})
        else:
            self.write({"status": "No files found to re-index in the specified folders."})