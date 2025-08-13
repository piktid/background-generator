import os
import requests
import json
from io import BytesIO
import base64
from PIL import Image, ImageFile, ImageFilter, ImageCms
import copy
from time import sleep


# -----------READ/WRITE FUNCTIONS------------
def open_image_from_url(url):
    response = requests.get(url, stream=True)
    if not response.ok:
        print(response)

    image = Image.open(BytesIO(response.content))
    return image


def open_image_from_path(path):
    f = open(path, 'rb')
    buffer = BytesIO(f.read())
    image = Image.open(buffer)
    return image

    return BytesIO(response.content)


def im_2_B(image):
    # Convert Image to buffer
    buff = BytesIO()

    if image.mode == 'CMYK':
        image = ImageCms.profileToProfile(image, 'ISOcoated_v2_eci.icc', 'sRGB Color Space Profile.icm', renderingIntent=0, outputMode='RGB')

    image.save(buff, format='PNG',icc_profile=image.info.get('icc_profile'))
    img_str = buff.getvalue()
    return img_str


def im_2_buffer(image):
    # Convert Image to bytes 
    buff = BytesIO()

    if image.mode == 'CMYK':
        image = ImageCms.profileToProfile(image, 'ISOcoated_v2_eci.icc', 'sRGB Color Space Profile.icm', renderingIntent=0, outputMode='RGB')

    image.save(buff, format='PNG',icc_profile=image.info.get('icc_profile'))
    return buff


def b64_2_img(data):
    # Convert Base64 to Image
    buff = BytesIO(base64.b64decode(data))
    return Image.open(buff)
    

def im_2_b64(image):
    # Convert Image 
    buff = BytesIO()
    image.save(buff, format='PNG')
    img_str = base64.b64encode(buff.getvalue()).decode('utf-8')
    return img_str


# -----------PROCESSING FUNCTIONS------------
def start_call(email, password, server_mode='production'):
    # Get token
    if server_mode == 'production':
        URL_API = 'https://api.piktid.com/api'
    else:
        print('Error server mode, exiting..')
        return {}
    print(f'Logging to: {URL_API}')

    response = requests.post(URL_API+'/tokens', data={}, auth=(email, password))
    response_json = json.loads(response.text)
    ACCESS_TOKEN = response_json['access_token']
    REFRESH_TOKEN = response_json['refresh_token']

    return {'access_token': ACCESS_TOKEN, 'refresh_token': REFRESH_TOKEN, 'url_api': URL_API}


def refresh_call(TOKEN_DICTIONARY):
    # Get token using only access and refresh tokens, no mail and psw
    URL_API = TOKEN_DICTIONARY.get('url_api')
    response = requests.put(URL_API+'/tokens', json=TOKEN_DICTIONARY)
    response_json = json.loads(response.text)
    ACCESS_TOKEN = response_json['access_token']
    REFRESH_TOKEN = response_json['refresh_token']

    return {'access_token': ACCESS_TOKEN, 'refresh_token': REFRESH_TOKEN, 'url_api': URL_API}


def resume_call(ACCESS_TOKEN, REFRESH_TOKEN):

    URL_API = 'https://api.piktid.com/api'

    return {'access_token': ACCESS_TOKEN, 'refresh_token': REFRESH_TOKEN, 'url_api': URL_API}


# UPLOAD ENDPOINTS
def upload_target_call(PARAM_DICTIONARY, TOKEN_DICTIONARY):

    OPTIONS_DICT = PARAM_DICTIONARY.get('OPTIONS', {})

    # start the generation process given the image parameters
    TOKEN = TOKEN_DICTIONARY.get('access_token', '')
    URL_API = TOKEN_DICTIONARY.get('url_api')

    target_full_path = PARAM_DICTIONARY.get('INPUT_PATH')
    if target_full_path is None:
        target_url = PARAM_DICTIONARY.get('INPUT_URL')
        """
        image_response = requests.get(target_url)
        image_response.raise_for_status()  
        image_file = BytesIO(image_response.content)
        image_file.name = 'target.jpg' 
        """
        # request with url
        response = requests.post(URL_API+'/edit/target', 
                                 headers={'Authorization': 'Bearer '+TOKEN},
                                 data={'url': target_url, 'options': json.dumps(OPTIONS_DICT)},
                                 )

        if response.status_code == 401:
            TOKEN_DICTIONARY = refresh_call(TOKEN_DICTIONARY)
            TOKEN = TOKEN_DICTIONARY.get('access_token', '')
            # try with new TOKEN
            response = requests.post(URL_API+'/edit/target', 
                                     headers={'Authorization': 'Bearer '+TOKEN},
                                     data={'url': target_url, 'options': json.dumps(OPTIONS_DICT)},
                                     )
    else:
        image_file = open(target_full_path, 'rb')
        # request with file
        response = requests.post(URL_API+'/edit/target', 
                                 headers={'Authorization': 'Bearer '+TOKEN},
                                 files={'file': image_file},
                                 data={'options': json.dumps(OPTIONS_DICT)},
                                 )

        if response.status_code == 401:
            TOKEN_DICTIONARY = refresh_call(TOKEN_DICTIONARY)
            TOKEN = TOKEN_DICTIONARY.get('access_token', '')
            # try with new TOKEN
            response = requests.post(URL_API+'/edit/target', 
                                     headers={'Authorization': 'Bearer '+TOKEN},
                                     files={'file': image_file},
                                     data={'options': json.dumps(OPTIONS_DICT)},
                                     )

    response_json = json.loads(response.text)
    print(f"Upload successful")

    return response_json


def upload_reference_call(PARAM_DICTIONARY, TOKEN_DICTIONARY):

    reference_full_path = PARAM_DICTIONARY.get('REF_PATH')
    if reference_full_path is None:
        reference_url = PARAM_DICTIONARY.get('REF_URL')
        image_response = requests.get(reference_url)
        image_response.raise_for_status()  
        image_file = BytesIO(image_response.content)
        image_file.name = 'reference.jpg' 
    else:
        image_file = open(reference_full_path, 'rb')

    # start the generation process given the image parameters
    TOKEN = TOKEN_DICTIONARY.get('access_token', '')
    URL_API = TOKEN_DICTIONARY.get('url_api')

    response = requests.post(URL_API+'/edit/reference', 
                             headers={'Authorization': 'Bearer '+TOKEN},
                             files={'reference': image_file},
                             )

    if response.status_code == 401:
        TOKEN_DICTIONARY = refresh_call(TOKEN_DICTIONARY)
        TOKEN = TOKEN_DICTIONARY.get('access_token', '')
        # try with new TOKEN
        response = requests.post(URL_API+'/edit/reference', 
                                 headers={'Authorization': 'Bearer '+TOKEN},
                                 files={'reference': image_file},
                                 )

    response_json = json.loads(response.text)
    print(f"Upload reference successful")

    return response_json


def generate_background_call(PARAM_DICTIONARY, TOKEN_DICTIONARY):

    ID_IMAGE = PARAM_DICTIONARY.get('ID_IMAGE')
    PROMPT = PARAM_DICTIONARY.get('PROMPT')
    CATEGORY = PARAM_DICTIONARY.get('CATEGORY')
    KEYWORD = PARAM_DICTIONARY.get('KEYWORD')

    data = {
            'id_image': ID_IMAGE
        }
    
    if CATEGORY is not None:
        data = {**data, 'keyword': json.dumps({CATEGORY: KEYWORD})}

    if PROMPT is not None:
        data = {**data, 'prompt': PROMPT}


    SEED = PARAM_DICTIONARY.get('SEED')
    PROMPT_STRENGTH = PARAM_DICTIONARY.get('PROMPT_STRENGTH')
    RELIGHT_STRENGTH = PARAM_DICTIONARY.get('RELIGHT_STRENGTH')
    USE_REFINER = PARAM_DICTIONARY.get('USE_REFINER', False)

    OPTIONS_DICT = PARAM_DICTIONARY.get('OPTIONS', {})

    REF_NAME = OPTIONS_DICT.get('reference_name')

    if PROMPT_STRENGTH is not None:
        OPTIONS_DICT = {**OPTIONS_DICT, 'strength': PROMPT_STRENGTH}

    if RELIGHT_STRENGTH is not None:
        OPTIONS_DICT = {**OPTIONS_DICT, 'relight_strength': RELIGHT_STRENGTH}

    if SEED is not None:
        OPTIONS_DICT = {**OPTIONS_DICT, 'seed': SEED}

    if REF_NAME is not None:
        OPTIONS_DICT = {**OPTIONS_DICT, 'reference_name': REF_NAME}

    if USE_REFINER:
        OPTIONS_DICT = {**OPTIONS_DICT, 'use_refiner': True}

    data = {**data, 'options': json.dumps(OPTIONS_DICT)}

    print(f'data to send to generation: {data}')

    # start the generation process given the image parameters
    TOKEN = TOKEN_DICTIONARY.get('access_token', '')
    URL_API = TOKEN_DICTIONARY.get('url_api')

    response = requests.post(URL_API+'/edit/background',
                             headers={'Authorization': 'Bearer '+TOKEN},
                             json=data
                             )
    # if the access token is expired
    if response.status_code == 401:
        TOKEN_DICTIONARY = refresh_call(TOKEN_DICTIONARY)
        TOKEN = TOKEN_DICTIONARY.get('access_token', '')
        # try with new TOKEN
        response = requests.post(URL_API+'/edit/background',
                                 headers={'Authorization': 'Bearer '+TOKEN},
                                 json=data
                                 )

    # print(response.text)
    response_json = json.loads(response.text)
    return response_json


# -----------NOTIFICATIONS FUNCTIONS------------
def get_notification_by_name(name_list, TOKEN_DICTIONARY):
    # name_list='new_generation, progress, error'
    TOKEN = TOKEN_DICTIONARY.get('access_token', '')
    URL_API = TOKEN_DICTIONARY.get('url_api')

    response = requests.post(URL_API+'/notification_by_name_json',
                             headers={'Authorization': 'Bearer '+TOKEN},
                             json={'name_list': name_list},
                             # timeout=100,
                             )
    # if the access token is expired
    if response.status_code == 401:
        # try with new TOKEN
        TOKEN_DICTIONARY = refresh_call(TOKEN_DICTIONARY)
        TOKEN = TOKEN_DICTIONARY.get('access_token', '')
        response = requests.post(URL_API+'/notification_by_name_json',
                                 headers={'Authorization': 'Bearer '+TOKEN},
                                 json={'name_list': name_list},
                                 # timeout=100,
                                 )
    # print(response.text)
    response_json = json.loads(response.text)
    return response_json.get('notifications_list')


def delete_notification(notification_id, TOKEN_DICTIONARY):
    TOKEN = TOKEN_DICTIONARY.get('access_token','')
    URL_API = TOKEN_DICTIONARY.get('url_api')

    print(f'notification_id: {notification_id}')
    response = requests.delete(URL_API+'/notification/delete_json',
                            headers={'Authorization': 'Bearer '+TOKEN},
                            json={'id': notification_id},
                            # timeout=100,
                            )
    # if the access token is expired
    if response.status_code == 401:
        # try with new TOKEN
        TOKEN_DICTIONARY = refresh_call(TOKEN_DICTIONARY)
        TOKEN = TOKEN_DICTIONARY.get('access_token', '')
        response = requests.delete(URL_API+'/notification/delete_json',
            headers={'Authorization': 'Bearer '+TOKEN},
            json={'id':notification_id},
            #timeout=100,
        )

    # print(response.text)
    return response.text


def handle_notifications(PARAM_DICTIONARY, TOKEN_DICTIONARY):

    ID_IMAGE = PARAM_DICTIONARY.get('ID_IMAGE')

    # check notifications to verify the generation status
    i = 0
    while i < 120:  # max 120 iterations -> then timeout
        i = i+1
        notifications_list = get_notification_by_name('edit_background', TOKEN_DICTIONARY)
        print(notifications_list)
        notifications_to_remove = [n for n in notifications_list if (n.get('name') == 'edit_background' and n.get('data').get('address') == ID_IMAGE)]

        print(f'notifications_to_remove: {notifications_to_remove}')
        # remove notifications
        result_delete = [delete_notification(n.get('id'), TOKEN_DICTIONARY) for n in notifications_to_remove]
        print(result_delete)

        if len(notifications_to_remove) > 0:
            print(f'download for image_id {ID_IMAGE} completed')
            return True, {**notifications_to_remove[0].get('data', {})}

        # wait
        print('waiting for notification...')
        sleep(5)

    return False, {}
