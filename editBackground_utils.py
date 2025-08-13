import os
import sys
import json
import requests
from io import BytesIO
from PIL import Image, ImageFile, ImageFilter
from random import randint

from editBackground_api import upload_target_call, upload_reference_call, generate_background_call, open_image_from_url, handle_notifications
from editBackground_dict import valid_keywords as bg_dict


def find_key_by_value(target_value):
    for key, values in bg_dict.items():
        if target_value in values:
            return key
    return None


def generate_background(PARAM_DICTIONARY, TOKEN_DICTIONARY):

    ID_IMAGE = PARAM_DICTIONARY.get('ID_IMAGE')

    REF_NAME = PARAM_DICTIONARY.get('REF_NAME')
    REF_PATH = PARAM_DICTIONARY.get('REF_PATH')
    REF_URL = PARAM_DICTIONARY.get('REF_URL')
    
    if REF_NAME is None and (REF_PATH is not None or REF_URL is not None):
        print('Uploading the reference image')
        response_json = upload_reference_call(PARAM_DICTIONARY=PARAM_DICTIONARY, TOKEN_DICTIONARY=TOKEN_DICTIONARY)
        REF_NAME = response_json.get('reference_name')
        print(f'ref_name: {REF_NAME}')
        if REF_NAME is None:
            # server errors
            print('Server error, try again later')
            return False, ''
        PARAM_DICTIONARY['OPTIONS']['reference_name'] = REF_NAME

    else:
        print(f'Reference is already available with code:{REF_NAME}, proceeding..')

    if ID_IMAGE is None:
        print('Uploading the target image')
        response_json = upload_target_call(PARAM_DICTIONARY=PARAM_DICTIONARY, TOKEN_DICTIONARY=TOKEN_DICTIONARY)
        ID_IMAGE = response_json.get('id_image')
        PARAM_DICTIONARY['ID_IMAGE'] = ID_IMAGE
    else:
        print(f'Input image is already available with code: {ID_IMAGE}, proceeding..')

    KEYWORD = PARAM_DICTIONARY.get('KEYWORD')
    if KEYWORD is not None:
        category = find_key_by_value(KEYWORD)
        if category is None:
            print(f'Error: keyword {KEYWORD} is not valid, please check the file editBackground_dict.py')
            return False
        print(f'Generating a new background using the category: {category} and keyword: {KEYWORD}')
        PARAM_DICTIONARY['CATEGORY'] = category
    else:
        PROMPT = PARAM_DICTIONARY.get('PROMPT')
        if PROMPT is not None:
            print(f'Generating a new background using the prompt: {PROMPT}')
        else:
            print('Error: prompt is not provided')
            return False

    response_json = generate_background_call(PARAM_DICTIONARY=PARAM_DICTIONARY, TOKEN_DICTIONARY=TOKEN_DICTIONARY)
    print(response_json)

    flag_response, response_notifications = handle_notifications(PARAM_DICTIONARY, TOKEN_DICTIONARY)
    if flag_response is False:
        # Error
        print('Error retrieving the generated images. No images found after 120 attempts')
        return False

    # Get the first link from the response
    download_link = ((response_notifications.get("links"))[0]).get("l") 
    print('new image ready for download:', download_link)

    flag_save, final_path = save_replaced_img(download_link, PARAM_DICTIONARY, TOKEN_DICTIONARY)
    if flag_save is False:
        print('Error: failed to save the generated image')
        return False, None, ID_IMAGE

    return flag_save, final_path, ID_IMAGE


def save_replaced_img(link, PARAM_DICTIONARY, TOKEN_DICTIONARY):
    print('Saving the generated image')
    try:
        options_str = ''
        seed = PARAM_DICTIONARY.get('SEED', 0)
        prompt = PARAM_DICTIONARY.get('PROMPT', None)
        if prompt is not None:
            options_str = options_str+prompt+'_'

        keyword = PARAM_DICTIONARY.get('KEYWORD', None)
        if keyword is not None:
            options_str = options_str+keyword+'_'
            
        ps = PARAM_DICTIONARY.get('PROMPT_STRENGTH')
        if ps is not None:
            options_str = options_str+'ps'+str(ps)+'_'
        
        if PARAM_DICTIONARY.get('USE_REFINER', False):
            options_str = options_str+'refined_'
        
        path_output = PARAM_DICTIONARY.get('OUTPUT_PATH', None)

        if PARAM_DICTIONARY.get('INPUT_PATH', None) is not None:
            filename_with_extension = PARAM_DICTIONARY.get('INPUT_PATH')
        elif PARAM_DICTIONARY.get('INPUT_URL', None) is not None:
            filename_with_extension = PARAM_DICTIONARY.get('INPUT_URL')
        else:
            filename_with_extension = link
        
        if path_output is None:
            path_output = os.path.abspath(os.getcwd())
        
        img_format = filename_with_extension.split('.')[-1]
        image_path = os.path.join(path_output, filename_with_extension.split('/')[-1])
        final_path = image_path.split('.')[0]+'_'+str(seed)+'_'+options_str+'.'+img_format
        print(f'Final path: {final_path}')

        # save the generated image in the generated folder
        src_img = open_image_from_url(link)
        try:
            src_img.save(final_path, subsampling=0, quality=95, icc_profile=src_img.info.get('icc_profile'))
        except:
            src_img.save(final_path)
    except Exception as e:
        print(f'Error: {e}')
        return False, None

    return True, final_path
 