import discord
import dotenv 

import requests 

import openai 

from discord.ext import commands 
import os 

import io 

from PIL import Image 


config = dotenv.load_dotenv(); 

class Bot(commands.Bot): 
  async def on_ready(self): 
    await self.tree.sync() 
    await self.change_presence(
      activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="Developer"
        )
      )
    
    print(f'Logged in as {self.user}') 

class Button(discord.ui.Button): 
  def __init__(self, id, link='', type='v', **args): 

    self.id = id
    self.link = link 
    self._type = type 

    super().__init__(**args) 

  async def callback(self, inter:discord.Interaction):

    match(self._type): 
      case 'v': 

        await inter.response.edit_message(content=f"Creating variations for image {self.id}") 

        data = requests.get(self.link)

        num_images = 4; 

        res = openai.Image.create_variation(
          image=data.content, 
          n=num_images, 
          size="1024x1024"
        )

        view = View(num=num_images, data=res['data']) 

        await inter.followup.send(view=view, embeds=[discord.Embed(url="https://heyitsmass.dev/").set_image(url=r['url']) for r in res['data']]); 

      case 'u': 
        await inter.response.edit_message(content=f"Creating upscale for image {self.id}") 

        data = requests.get(self.link)

        base_img = Image.open(io.BytesIO(data.content))

        base_img.resize((4096, 4096), resample=Image.BOX).save("new_img.png", "png", optimize=True) 

        with open('new_img.png', 'rb') as f: 
          
          await inter.followup.send(file=discord.File(f), ephemeral=True)

        os.remove('new_img.png')

      case _: 
        raise RuntimeError(f"Unknown type: '{type}' *** this is an internal error ***")

class View(discord.ui.View): 
  def __init__(self, num=0, data=[], **args): 
    super().__init__(**args)

    for i in range(num): 
      super().add_item(Button(label=f"V{i}", row=0, type='v', link=data[i]['url'], id=i))

    for i in range(num): 
      super().add_item(Button(label=f"U{i}", row=1, type='u', link=data[i]['url'], id=i)) 

      
intents = discord.Intents.default() 
intents.message_content = True 
intents.reactions = True 

bot = Bot(intents=intents, command_prefix="$") 

@bot.tree.command(description="imagine something?!?") 
async def imagine(inter:discord.Interaction, prompt:str): 


  await inter.response.send_message(f"Generating response for prompt: {prompt}", ephemeral=True); 

  num_images = 4 

  res = openai.Image.create(
    prompt=prompt, 
    n=num_images, 
    size="1024x1024"
  )


  view = View(num=num_images, data=res['data']) 

  
  await inter.followup.send(view=view, embeds=[discord.Embed(url="https://heyitsmass.dev/").set_image(url=r['url']) for r in res['data']]); 
  
openai.api_key = os.environ['OPEN_AI_TOKEN']
bot.run(os.environ['DISCORD_TOKEN'])

