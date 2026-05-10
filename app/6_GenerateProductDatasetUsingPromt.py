from dotenv import load_dotenv
import anthropic
import os
import csv
from io import StringIO
from datetime import datetime, timezone
load_dotenv()

# Check if an Anthropic API key is valid without using message credits.
def validateKey(api_key):
    if api_key is None or api_key.strip() == "":
        return False

    try:
        client = anthropic.Anthropic(api_key=api_key)
    except anthropic.AuthenticationError:
        return False
    return client

def getClient():
    client = validateKey(os.getenv("ANTHROPIC_API_KEY"))
    if client:
        print("Valid API Key. Proceeding with the application...")
        return client
    else:
        return None

def getModel(client, model_name):
    haikuModel = ''
    try:
        models = client.models.list()
        for model in models.data:
            if model_name in model.id.lower():
                haikuModel = model.id
    except Exception as e:
        print(f"Error retrieving the '{model_name}' model: {e}")
        return None
    print(f"Using model: {haikuModel}")
    print('------------------------------------------')
    return haikuModel
    
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages, client, model, system_instruction=None, stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 10000,
        "messages": messages,
        "temperature": 1.0,
        "stream": False
    }
    if system_instruction:
        params["system"] = system_instruction
        
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
        
    response = client.messages.create(**params)
    print("AI Assistant: ", response.content[0].text, end="", flush=True)
    return response.content[0].text

def generate_product_dataset(client, model):
    prompt = """
Generate an evaluation dataset for a prompt evaluation.
The dataset will be used to create a csv file that will be imported to Magento2 and create products.
Generate an csv file with columns as Magento2 product attributes.
Consider all out of the box product attributes

Example output:
```csv
sku,store_view_code,attribute_set_code,product_type,categories,product_websites,name,description,short_description,weight,product_online,tax_class_name,visibility,price,special_price,special_price_from_date,special_price_to_date,url_key,meta_title,meta_keywords,meta_description,created_at,updated_at,new_from_date,new_to_date,display_product_options_in,map_price,msrp_price,map_enabled,gift_message_available,custom_design,custom_design_from,custom_design_to,custom_layout_update,page_layout,product_options_container,msrp_display_actual_price_type,country_of_manufacture,additional_attributes,qty,out_of_stock_qty,use_config_min_qty,is_qty_decimal,allow_backorders,use_config_backorders,min_cart_qty,use_config_min_sale_qty,max_cart_qty,use_config_max_sale_qty,is_in_stock,notify_on_stock_below,use_config_notify_stock_qty,manage_stock,use_config_manage_stock,use_config_qty_increments,qty_increments,use_config_enable_qty_inc,enable_qty_increments,is_decimal_divided,website_id,deferred_stock_update,use_config_deferred_stock_update,related_skus,crosssell_skus,upsell_skus,hide_from_product_page,custom_options,bundle_price_type,bundle_sku_type,bundle_price_view,bundle_weight_type,bundle_values,associated_skus\n
MD100001,,Default,simple,"Default Category/Gear,Default Category/Gear/Fitness Equipment",base,Sprite Yoga Strap 6 foot,"<p>The Sprite Yoga Strap is your untiring partner in demanding stretches, holds and alignment routines. The strap's 100% organic cotton fabric is woven tightly to form a soft, textured yet non-slip surface. The plastic clasp buckle is easily adjustable, lightweight and urable under strain.</p><ul><li>100% soft and durable cotton.<li>Plastic cinch buckle is easy to use.<li>Three natural colors made from phthalate and heavy metal free dyes.</ul>",,1,1,Taxable Goods,"Catalog, Search",14,,,,sprite-yoga-strap-6-foot,Meta Title,"meta1, meta2, meta3",meta description,"2015-10-25 03:34:20","2015-10-25 03:34:20",,,Block after Info Column,,,,,,,,,,,Use config,,"has_options=1,quantity_and_stock_status=In Stock,required_options=0",100,0,1,0,0,1,1,0,0,1,1,,1,0,1,1,0,1,0,0,1,0,1,"24-WG087,24-WG086","24-WG087,24-WG086","24-WG087,24-WG086",,"name=Custom Yoga Option,type=drop_down,required=0,price=10.0000,price_type=fixed,sku=,option_title=Gold|name=Custom Yoga Option,type=drop_down,required=0,price=10.0000,price_type=fixed,sku=,option_title=Silver|name=Custom Yoga Option,type=drop_down,required=0,price=10.0000,price_type=fixed,sku=yoga3sku,option_title=Platinum",,,,,,\n
...
```

* Focus on creation of sample products
* Focus on including all attributes
* Focus on lates magento2 version suport
* Focus on generating realistic data for each attribute
* Do no include empty rows in the csv output

Please generate 2 products data.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```csv")
    text = chat(messages, client, model, stop_sequences=["```"])
    return text

def main():
    client = getClient()
    if (not client):
        print("Invalid API Key. Please check your .env file.")
        return

    haikuModel = getModel(client, 'haiku')
    if (not haikuModel):
        print("Could not find the 'haiku' model. Please check your model availability.")
        return

    # Generate a dataset using claude
    dataset_text = generate_product_dataset(client, haikuModel)
    if not dataset_text:
        print("No dataset returned from model.")
        return
    print(dataset_text)

    # Clean possible code fences and trim whitespace
    cleaned = dataset_text.strip()
    lines = cleaned.splitlines()
    cleaned = "\n".join(lines).strip()

    # Parse CSV text into rows then write to file
    csv_io = StringIO(cleaned)
    reader = csv.reader(csv_io)
    with open('products.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in reader:
            # if (row == '\n'):  # Skip empty rows
            #     continue
            # Removed this check as the model should not generate empty rows, and we want to preserve any rows that may have empty fields but are not entirely empty.
            writer.writerow(row)
    print('Products dataset file created successfully!')

if __name__ == "__main__":
    main()