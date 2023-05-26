from utils.utils import *
import pickle as pk
import argparse
import os
from sklearn import preprocessing
import random


def get_binary_vec(current_cats: list, all_cats: list): 
    #getting the simple binary representation of the user's selected categories
    #[0,0,0,0,1,0,0,0,1,1,0..]
    lb = preprocessing.LabelBinarizer()
    lb.fit(all_cats)
    return list(sum(lb.transform(current_cats)))

def get_vecs(likes, dislikes, all_cats): 
    #getting a binary representation of the categories of likes and dislikes
    if len(likes)!=0:
        likes_vec=get_binary_vec(likes, all_cats)
    else:
        likes_vec=[0 for i in range(0, len(all_cats))]
    if len(dislikes)!=0:
        dis_vec=get_binary_vec(dislikes,all_cats)
    else:
        dis_vec=[0 for i in range(0, len(all_cats))]
    
    return likes_vec + dis_vec

def get_prof_vec_dict(profiles, all_cats): 
    #profiles vectorization (only categories)
    prof_vec_dict={}
    for i in list(profiles.keys()):
        like_cats=[]
        dis_cats=[]
        for cat in list(profiles[i].keys()):
            if len(profiles[i][cat][0]) !=0:
                like_cats.append(cat)
            if len(profiles[i][cat][1])!=0:
                dis_cats.append(cat)
    
        prof_vec_dict[i]=get_vecs(like_cats, dis_cats, all_cats)
    return prof_vec_dict


def get_same_others(target:dict, profiles_dict:dict, same_ids:list):    
    #getting links to images by categories that are in the favorites of the target 
    #and those that are not there, but they are present in the favorites of similar users
    target_cats =[i for i in list(target.keys())]    
    same_dict={}
    other_dict={}
    for iD in same_ids:        
        same_profile=profiles_dict[iD]
        for cat in list(same_profile.keys()):            
            if cat in target_cats:
                #adding to the list of images that are not in the likes or dislikes of the target
                links=[link for link in same_profile[cat][0] 
                                  if link not in target[cat][0] 
                                  and link not in target[cat][1]]
                if len(links)>0:
                    if cat in list(same_dict.keys()):
                        #if the category is already in the dictionary, add new values to its values
                        same_dict[cat]=same_dict[cat]+[i for i in links if i not in same_dict[cat]]
                    else:    
                        #if the category is not in the dictionary, add links as is
                        same_dict[cat]=links
            else:
                if len(same_profile[cat][0])>0:
                    if cat in list(other_dict.keys()):
                        #if the category is already in the dictionary, add new values to its values
                        other_dict[cat]=other_dict[cat]+[i for i in same_profile[cat][0] if i not in other_dict[cat]]
                    else:
                        #if the category is not in the dictionary, add links as is
                        other_dict[cat]=same_profile[cat][0]

    return same_dict, other_dict

def get_im_lists(img_adress_dict, feutures_dict_adresses, same_size: int=50, return_size: int=10): 
    #getting lists of recommended images by category
    cats_img_dict={}
    for cat in list(img_adress_dict.keys()):
        for adress in feutures_dict_adresses:
            if cat == adress.split('/')[-1].split('.')[0]:
                feutures_dict=pk.load(open(adress, 'rb'))                              
                    
                cats_img_dict[cat]=get_shuffled_same_list(cat, img_adress_dict, feutures_dict, same_size, return_size)

    return cats_img_dict


def get_shuffled_same_list(cat, img_adress_dict, feutures_dict, same_size, return_size):
    #getting a shuffled list of images similar to those in favorites of similar users
    imgs=[]
    for img_adress in img_adress_dict[cat]:  
        #getting a large sample
        indx, distance=get_distance_and_index(feutures_dict['/root/PhotoFlow_Server/static'+img_adress], feutures_dict)

        #getting a limited number of random images from a large sample
        if len(indx[0])>same_size:            
            indx=random.choices(indx[0][1:same_size+1], k=return_size)
        else:
            indx=random.choices(indx[0][1:len(indx[0])], k=len(indx[0][1:len(indx[0])]))
        
        #packing list
        for i in indx:
            same_img_adress=list(feutures_dict.keys())[i]
            if same_img_adress not in imgs:
                imgs.append(list(feutures_dict.keys())[i])
        
    return imgs
  

def get_other_sames_by_target_likes(target, means_dict, feutures_dict_adress):
    #getting a small number of images similar to those in the favorites of the target 
    #from categories that are not in the favorites of the target
    imgs=[]
    for cat in list(target.keys()):
        for adress in feutures_dict_adress:
            
            if cat == adress.split('/')[-1].split('.')[0]:
                feutures_dict=pk.load(open(adress, 'rb'))
                for img_adress in target[cat][0]:
                    target_feutures=feutures_dict['/root/PhotoFlow_Server/static'+img_adress]
                    mean_indx, mean_distance=get_distance_and_index(target_feutures, means_dict)
                    
                    others_cat_f_adress_list=[list(means_dict.keys())[i] for i in mean_indx[0][1:4]]
                    

                    for other_cat_f in others_cat_f_adress_list:
                        other_feutures_dict=pk.load(open(other_cat_f, 'rb'))
                        indx, distance = get_distance_and_index(target_feutures, other_feutures_dict)
                        for i in indx[0][0:3]:
                          other_img_adress=list(other_feutures_dict.keys())[i]
                          
                          if other_img_adress not in imgs:
                              imgs.append(other_img_adress)
                  
    return dict.fromkeys(["others"], imgs)



def recommendation(user_id: str, users_dict_path: str, cat_list_as_str: str, split_char: str, 
                  full_stats_path:str, same_count: int, output_path: str, save_as_dict: bool, 
                  feutures_dicts_directory: str, cat_mean_dict_adress: str, same_size: int, return_size: int):

    #getting a dictionary of recommendations {cctegory:[links]} 
    #and saving it in the specified directory

    users_dict=open_dict(users_dict_path)

    if same_size<return_size:
        same_size=same_size*return_size    

    #get f_dict path per category
    feutures_dict_adresses=[feutures_dicts_directory+'/'+path for path in os.listdir(feutures_dicts_directory)]

    #if categories are not set explicitly, accept categories from the directory with feature map dictionaries
    if cat_list_as_str != None:
        cat_list=cat_list_as_str.split(split_char)
    else:
        cat_list=os.listdir(feutures_dicts_directory)
        for i in range(0,len(cat_list)):
            cat_list[i]=cat_list[i].replace('.pkl','')

    dim=2*len(cat_list)

    #similar users search
    users_vec_dict=get_prof_vec_dict(users_dict, cat_list)
    indx, _=get_distance_and_index(users_vec_dict[user_id], users_vec_dict, dim) 

    #getting target's favorites and dislikes, and same to 10 similar users
    target=users_dict[list(users_vec_dict.keys())[indx[0][0]]]
    same_ids=[list(users_vec_dict.keys())[i] for i in [j for j in indx[0][:10]]]

    #getting a list of images from the same categories as the target, as well as a list of images 
    #from selected categories of similar users that are not included in the selected target categories
    same_dict, other_dict=get_same_others(target, users_dict, same_ids) 

    #getting shuffled lists of images similar to featured images of similar users
    new_same_dict=get_im_lists(same_dict, feutures_dict_adresses, same_size, return_size)
    new_others_dict=get_im_lists(other_dict, feutures_dict_adresses, same_size, return_size)

    mean_dict=open_dict(cat_mean_dict_adress)

    #getting a dictionary with lists of images that are similar to those that are in the favorites of the target, 
    #but are in categories that do not belong to the favorites of the target
    same_others_dict=get_other_sames_by_target_likes(target, mean_dict, feutures_dict_adresses)
    #concat dicts
    result_dict={**new_same_dict, **new_others_dict, **same_others_dict}   

    #result as a string
    result=''
    for cat in list(result_dict.keys()):
        for path in result_dict[cat]:
            result+=path+','

    result=result[:-1]
    
    #save recommendations to a dictionary, or print as a string if it specified
    if save_as_dict:
        if output_path==None:
            if full_stats_path==None: 
                full_stats_path=users_dict_path
            new_path=os.path.dirname(os.path.realpath(full_stats_path))
            output_path=f"{new_path}/{user_id}_recomedation.pkl"
        pk.dump(result_dict, open(output_path,"wb"))
    else:
        print(result)


def arg_parse():
        
    parser = argparse.ArgumentParser(description='Get recomendation files list')
   
    parser.add_argument("--user_id", dest = 'user_id', help = 
                        "User id",
                        default = "", type = str)
    
    parser.add_argument("--path", dest = 'path', help = 
                        "Users like/dislike dict path: /directory/sub_directory/file_name.pkl",
                        default = "", type = str) 
    
    parser.add_argument("--cats", dest = 'cats', help = 
                        "Category list: 'cats,dogs,monkeys,orcs'",
                        default = None, type = str) 

    parser.add_argument("--seporator", dest = 'seporator', help = 
                        "Sign to separate category string: ','",
                        default = ",", type = str) 

    parser.add_argument("--stat_path", dest = 'stat_path', help = 
                        "way to save complete statistics (for further system improvement): /directory/sub_directory/file_name.pkl",
                        default = None, type = str) 
    
    parser.add_argument("--count", dest = 'count', help = 
                        "Specifies the length of the array with the names of the users for which the selection of recommendations is taken. "+ 
                        "If not specified, a sample is taken of all users available in the database. "+ 
                        "When you increase the quality does not change, just increases the array of recommendations.",
                        default = None, type = int)    
    
    parser.add_argument("--out", dest = 'out', help = 
                        "Output path: /directory/sub_directory/file_name.pkl",
                        default = None, type = str)
    
    parser.add_argument("--save_dict", dest = 'save_dict', help = 
                        "Save result as dict",
                        default = True, type = bool)

    parser.add_argument("--ims_f_dir", dest = 'ims_f_dir', help = 
                        "images features directory per category: /directory/sub_directory",
                        default = None, type = str)

    parser.add_argument("--mean_path", dest = 'mean_path', help = 
                        "Path to mean per categories: /directory/sub_directory/file_name.pkl",
                        default = None, type = str)

    parser.add_argument("--same_size", dest = 'same_size', help = 
                        "Number of similar images from which random images are taken in size = return_size: 50",
                        default = 50, type = int)

    parser.add_argument("--return_size", dest = 'return_size', help = 
                        "Number of images randomly selected from a sample = same_size, at each iteration: 10",
                        default = 10, type = int)
    
    return parser.parse_args()


if __name__ == '__main__':

    args=arg_parse()   

    recommendation(args.user_id, args.path, args.cats, args.seporator, args.stat_path, 
                  args.count, args.out, args.save_dict, args.ims_f_dir, args.mean_path, 
                  args.same_size, args.return_size)


