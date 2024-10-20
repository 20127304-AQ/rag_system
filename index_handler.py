from base_handler import BaseHandler
from utils import get_all_files_in_folder, index_code, get_db_and_table

# Handler for indexing task
class IndexHandler(BaseHandler):
    async def get(self):
        folder_path = self.get_argument('folder_path', 'data')
        user_id = self.current_user
        db, table_name = await get_db_and_table(user_id)
        
        files_to_index = get_all_files_in_folder(folder_path)
        if files_to_index:
            await index_code(files_to_index, db, table_name)
            self.write({"status": f"Indexing complete for {len(files_to_index)} files."})
        else:
            self.write({"status": "No files found to index."})