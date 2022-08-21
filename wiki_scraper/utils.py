EXCEPTIONAL = 'EXCEPTIONAL'


def infer_folder_name(article_name: str):
    folder_name = ''
    for ch in article_name:
        if str.isalpha(ch):
            folder_name += ch
            
        if len(folder_name) == 2:
            break
    if len(folder_name) == 0:
        return EXCEPTIONAL
    
    if len(folder_name) == 1:
        return folder_name + folder_name
    
    return folder_name
