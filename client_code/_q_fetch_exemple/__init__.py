from ._anvil_designer import _q_fetch_exempleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class _q_fetch_exemple(_q_fetch_exempleTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        #trainingsrecords
        training_record = app_tables.projects_files.search(
                                                            q.fetch_only(
                                                                        "file_id", "study_id", "task_id", "document_type", "version", 
                                                                        "file_name", "file_type", "creation_date","description", "updated_date",
                                                                        trainingsrecord_link=q.fetch_only("user_link"), 
                                                                        created_by=q.fetch_only("email"),
                                                                        updated_by=q.fetch_only("email")
                                                                       ),
                                                                tables.order_by('creation_date', ascending=False), 
                                                                study_id=study_id,
                                                                document_type='Training record'
                                                            )
