import anvil.server

#*****  Récup la liste du répertoire video via uplinks pi5: list_videos()
#         pour le chargement par dropdown des videos (QCM_visu_creation) 
@anvil.server.callable
def get_video_urls():
    videos_list = list_videos()
    return videos_list