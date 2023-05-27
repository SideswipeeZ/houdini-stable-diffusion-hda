import json
import requests
import math
import array
import io
import base64
from PIL import Image, PngImagePlugin
from datetime import date
import random
import string
import os
from PySide2 import QtNetwork

def unlock_multiline(node, parm):   
    # Get State 1=On 0=Off
    state = str(node.parm(parm+"_ml").eval())

    hda = node.type().definition()
    ptg = node.parmTemplateGroup()
    
    strParm = node.parm(parm)
    template = strParm.parmTemplate()
    template.setTags({"editor": state})
    
    ptg.replace(parm, template)
    hda.setParmTemplateGroup(ptg)
        

def test():
    print("TEST")

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])
    
def getRamUsage(ram,cuda):
    ram_free = convert_size(ram["free"])
    ram_total = convert_size(ram["total"])
    ram_str = "RAM: " + ram_free + " / " + ram_total 
    print(ram_str)
    
    vram_free = convert_size(cuda["free"])
    vram_total = convert_size(cuda["total"])
    vram_str = "VRAM: " + vram_free + " / " + vram_total
    print(vram_str)
    
    return vram_str + "\n" + ram_str
    
def checkResources(node):
    print("Checking Resource Usage...")
    # Build Address Info
    host = node.parm("sd_host").evalAsString()
    port = node.parm("sd_port").evalAsString()
    if host != "":
        # Valid logic
        if port != "":
            address = host+":"+port
        else:
            address = host
        conn = checkConnection(address, node)
        if conn == True:
            # Get Usage Info
            response = requests.get(url=f'{address}/sdapi/v1/memory')
            js = response.json()
            ram = js["ram"]
            cuda = js["cuda"]["system"]
            ram_str = getRamUsage(ram,cuda)
            node.parm("sd_ramUsage").set(ram_str)
    else:
        print("SD ERROR: Host Cannot be Blank...")
        
        
def connectSD(node):
    print("\n")
    print("Connecting to Stable Diffusion...")
    node.parm("sd_connected").set(0)
    # Build Address Info
    host = node.parm("sd_host").evalAsString()
    port = node.parm("sd_port").evalAsString()
    if host != "":
        # Valid logic
        if port != "":
            address = host+":"+port
        else:
            address = host
        conn = checkConnection(address, node)
        if conn == True:
            loadItems(address, node)
        else:
            print("Could Not Connect to SD... :(")
    else:
        print("SD ERROR: Host Cannot be Blank...")
        
def checkConnection(address, node):
    print("Attempting to Connect to: " +address)
    response = requests.get(url=f'{address}/app_id/')
    status = response.status_code
    if status == 200:
        print("Connected")
        node.parm("sd_connected").set(1)
        return True
    else:
        print("Not Connected")
        node.parm("sd_connected").set(0)
        return False
        
def loadItems(address,node):
    print("Loading Items")
    
    # Load Models
    print("    Loading Models")
    model_response = requests.get(url=f'{address}/sdapi/v1/sd-models')
    model_js = model_response.json()
    model_list = []
    for model in model_js:
        model_list.append(model["title"])
    
    hda = node.type().definition()
    ptg = node.parmTemplateGroup()
    
    menuParm = node.parm("sd_models")
    template = menuParm.parmTemplate()
    template.setMenuItems(model_list)
    template.setMenuLabels(model_list)
    
    ptg.replace("sd_models", template)
    hda.setParmTemplateGroup(ptg)
    ###
    
    #check for loaded model from SD
    # Get Model Loaded
    options = requests.get(url=f'{address}/sdapi/v1/options')
    model = options.json()["sd_model_checkpoint"]
    node.parm("sd_models").set(model)
    
    
    # Load Samplers
    print("    Loading Samplers")
    samplers_response = requests.get(url=f'{address}/sdapi/v1/samplers')
    samplers_js = samplers_response.json()
    samplers_list = []
    for sample in samplers_js:
        samplers_list.append(sample["name"])
    
    hda = node.type().definition()
    ptg = node.parmTemplateGroup()
    
    menuParm = node.parm("sd_sampler")
    template = menuParm.parmTemplate()
    template.setMenuItems(samplers_list)
    template.setMenuLabels(samplers_list)
    
    ptg.replace("sd_sampler", template)
    hda.setParmTemplateGroup(ptg)
    ###
    print("Loaded Items")

def buildAddress(node):
    # Build Address Info
    host = node.parm("sd_host").evalAsString()
    port = node.parm("sd_port").evalAsString()
    if host != "":
        # Valid logic
        if port != "":
            address = host+":"+port
        else:
            address = host
        conn = checkConnection(address, node)
        if conn == True:
            return address
        else:
            print("Could Not Connect to SD... :(")
    else:
        print("SD ERROR: Host Cannot be Blank...")
        return none
    
def changeModel(node):
    address = buildAddress(node)
    # Get Model Loaded
    options = requests.get(url=f'{address}/sdapi/v1/options')
    model = options.json()["sd_model_checkpoint"]
    
    if model == node.parm("sd_models").evalAsString():
        print("Model Already Selected.")
    else:
        print("Changing Model...")
        optionsJS = {"sd_model_checkpoint": node.parm("sd_models").evalAsString()}
        requests.post(url=f'{address}/sdapi/v1/options', json=optionsJS)
        print("Changed Model...")

def runSD(node):
    print("\nAttempting to Run...")
    address = buildAddress(node)
    if address:
        #change Model
        changeModel(node)
        payload = {
            "prompt": node.parm("sd_prompt").evalAsString(),
            "negative_prompt": node.parm("sd_negprompt").evalAsString(),
            "seed": node.parm("sd_seed").evalAsString(),
            "steps": node.parm("sd_sample_steps").evalAsString(),
            "cfg_scale": node.parm("sd_cfg").evalAsString(),
            "width": node.parm("sd_height").evalAsString(),
            "height": node.parm("sd_width").evalAsString(),
            "sampler_index": node.parm("sd_sampler").evalAsString()
            
        }
        num_tasks = 1
        with hou.InterruptableOperation(
        "Running Stable Diffusion Job.", open_interrupt_dialog=True) as operation:
            response = requests.post(url=f'{address}/sdapi/v1/txt2img', json=payload)
            js = response.json()
            saveFile(js,node, payload)

        
def saveFile(js,node, payload):
    image = Image.open(io.BytesIO(base64.b64decode(js["images"][0])))
    save_dir = node.parm("sd_saveDir").evalAsString()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if save_dir:
        name = str(date.today()) + "_" + "" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))+".png"
        fullPath = os.path.join(save_dir,name)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", json.dumps(payload))
        image.save(fullPath, pnginfo=pnginfo)
        fileCops = [x for x in hou.node(node.path()+"/cop2net1").children() if x.type().name() == "file"]
        if fileCops:
            for i in fileCops:
                i.parmTuple("filename").set((fullPath,""))
    print("Completed")
