import argparse
from pyexpat import features
import torch
import os
from PIL import Image
import pickle as pk
from tqdm import tqdm
from sklearn.neighbors import NearestNeighbors
from os import listdir
import numpy as np
import hnswlib


    

def is_in_dict(name: str, features_dict: dict):
    #checks if a file exists in a directory
    if name in list(features_dict.keys()):                
            return True
    return False


def is_in_folder(name: str, names: list):
    #checks if a key exists in a dirtionary
    if name in names:
            return True
    return False


def sync(name: list, features_dict: dict):                                     
    #checks if all the images specified in the dictionary are still available in the directory, 
    #if not, removes the excess from the dictionary
    for im_name in list(features_dict.keys()):                    
        if not is_in_folder(im_name, name):                
            try:
                del features_dict[im_name]
            except:
                continue   
            
            
def get_path(im_directory: str):
    #get the paths of all files in a directory and subdirectories 
    all_files=[]
    for directory, _subdirs, files in os.walk(im_directory):
        for name in files:
            all_files.append(os.path.join(directory, name))
    return all_files


def get_distance_and_index(querry, features_dict: dict, dim: int=512):  
    #getting an array with images features and
    #converting its to the appropriate format
    features=list(features_dict.values())   
    features=np.array(features)
    features=np.squeeze(features) 

    index = hnswlib.Index(space='l2', dim=dim)
    index.init_index(max_elements=10000, ef_construction=100, M=16)
    index.add_items(features)
    labels, distances = index.knn_query(querry, k = len(features))
    return labels, distances


def get_same(querry, features_dict: dict):

    #getting an array with file addresses from the rest of the selection
    file_names=list(features_dict.keys())
    
    indices, dist = get_distance_and_index(querry, features_dict) 
       
    #for using as variable in bash
    names_as_string=''
    for i in indices[0]:
        names_as_string+=file_names[i]+','

    print(names_as_string[:-1])
    

def open_dict(dict_adress: str):
    features_dict={}
    try:
        features_dict=pk.load(open(dict_adress, "rb"))
    except (OSError, IOError) as e:
        print("file_not_found")
    return features_dict
