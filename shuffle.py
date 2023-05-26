import random
import pickle as pk
import argparse
from utils.utils import *

def shuffle(rec_dict_path:str, cat_list_as_str: str, seporator:str, id_counter: int):
    #shuffles recommendations while maintaining relevance order
    rec_dict=open_dict(rec_dict_path)

    if cat_list_as_str != None:
        cat_list=cat_list_as_str.split(seporator)
    else: 
        cat_list=list(rec_dict.keys())

    cat_list.append('others')
    
    result=''
    adress_list=[]
    for cat in cat_list:
        if cat in list(rec_dict.keys()):
            adress_list=adress_list+rec_dict[cat]
    random.shuffle(adress_list)
    for adress in adress_list:
        result+=adress+','

    print(result[:-1])


def arg_parse():    
    
    parser = argparse.ArgumentParser(description='Shuffle recomendation')
   
    parser.add_argument("--dict_path", dest='dict_path', help=
                        "path to the recomendation dictionary file: /directory/sub_directory/usrt_id_recomendation.pkl",
                        default = None, type = str)

    parser.add_argument("--cats", dest = 'cats', help = 
                        "Category list as str: 'cats,dogs,monkeys,orcs'",
                        default = None, type = str)

    parser.add_argument("--seporator", dest = 'seporator', help = 
                        "Sign to separate category string: ','",
                        default = ",", type = str) 

    parser.add_argument("--id_counter", dest='id_counter', help=
                        "Limits the selection to form a recommendation string",
                        default = None, type = int)
    
    return parser.parse_args()


if __name__ == '__main__':

    args=arg_parse()    

    shuffle(args.dict_path, args.cats, args.seporator, args.id_counter)