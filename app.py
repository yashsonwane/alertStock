import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests



st.set_page_config(layout = 'wide', initial_sidebar_state='collapsed')

credentials_path = 'key.json' 

############# read Gsheet #############
def read_gsheet(credentials_path):
  # Set up the credentials
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
  gc = gspread.authorize(credentials)

  # Open the Google Sheet using its title or URL
  spreadsheet = gc.open('Stock')

  # Select a specific worksheet by title
  worksheet = spreadsheet.worksheet('Sheet1')

  # Get all values from the worksheet
  values = worksheet.get_all_values()

  # Convert the data to a Pandas DataFrame
  df = pd.DataFrame(values[1:], columns=values[0])

  return df, worksheet

############# change flag #############
def change_flag_status(worksheet,row_number,new_value):
    """Updates cell value with new_value.

    """
    # Defines the cell to update using row_number and a hardcoded column ('O')
    cell_to_update = f"O{row_number+2}"  

    # Updates the specified cell with new_value
    worksheet.update_acell(cell_to_update, new_value)

#############  #############

def escape_special_characters(text, special_characters= ["|","(","=",")",".",",","[","!","]","{","}","_","+","@","#","$","%",":",";","/",">","<","-"]):
    # iterate over special characters
    for char in special_characters:
        # if character is present in text
        if char in text:
            # replace it with escaped character
            text = text.replace(char, "\\" + char)
    # return modified text
    return text

#############  #############
def send_message(message):
    """Function to send message."""

    bot_token = '6619777004:AAFX4CnYdKZMfpniA04OSCfZN4-VxSXT8-w'
    channel_id = '-1002033009847' # Group ID "testt"
    bot_message = escape_special_characters(message)

    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={channel_id}&parse_mode=MarkdownV2&text={bot_message}'

    response = requests.get(send_text)
    return response.content

#############  #############

def message_for_target3(stock_name,recommended_date,recommended_price,target1,target2,target3,ROI):
  # Compose Telegram message for target3 achieved
  message_for_telegram_for_targert3_achive = f"""*{stock_name.upper()}* stock recommend to our premium group members. 
  On *{recommended_date}* at price *{recommended_price}*
  Target 1- *{target1}* Achieved ! ✅
  Target 2- *{target2}* Achieved ! ✅
  Target 3- *{target3}* Achieved ! ✅
  *{ROI}%* Returns. """
  # Send message to Telegram group
  response = send_message(message_for_telegram_for_targert3_achive)
  # Print message and response to console
  st.write(message_for_telegram_for_targert3_achive)
  st.write(response)


def message_for_target2(stock_name,recommended_date,recommended_price,target1,target2,target3,ROI):
  # Compose Telegram message for target2 achieved
  message_for_telegram_for_targert2_achive = f"""*{stock_name.upper()}* stock recommend to our premium group members. 
  On *{recommended_date}* at price *{recommended_price}*
  Target 1- *{target1}* Achieved ! ✅
  Target 2- *{target2}* Achieved ! ✅
  *{ROI}%* Returns. """
  response = send_message(message_for_telegram_for_targert2_achive)
  st.write(message_for_telegram_for_targert2_achive)
  st.write(response)

def message_for_target1(stock_name,recommended_date,recommended_price,target1,target2,target3,ROI):
  # Compose Telegram message for target1 achieved
  message_for_telegram_for_targert1_achive = f"""*{stock_name.upper()}* stock recommend to our premium group members. 
  On *{recommended_date}* at price *{recommended_price}*
  Target 1- *{target1}* Achieved ! ✅
  *{ROI}%* Returns. """
  response = send_message(message_for_telegram_for_targert1_achive)
  st.write(message_for_telegram_for_targert1_achive)
  st.write(response)

def sub_process(target_achive_df,worksheet,target_point,flag_status):
  if not target_achive_df.empty:
    for row in range(len(target_achive_df)):
      stock_name = target_achive_df["Stock Name"].iloc[row]
      recommended_date = target_achive_df["Recommendation Date"].iloc[row]
      recommended_price = target_achive_df["Recommended Price"].iloc[row]
      target1 = target_achive_df["Target 1"].iloc[row]
      target2 = target_achive_df["Target 2"].iloc[row]
      target3 = target_achive_df["Target 3"].iloc[row]
      ROI = str(round(((float(target_achive_df[f"Target {target_point}"].iloc[row])-float(target_achive_df["Recommended Price"].iloc[row]))/float(target_achive_df["Recommended Price"].iloc[row]))*100,2))
      row_number = target_achive_df.index[row]
      print(target_achive_df.iloc[row])
      
      if target_point == 3:
        message_for_target3(stock_name,recommended_date,recommended_price,target1,target2,target3,ROI)
      if target_point == 2:
        message_for_target2(stock_name,recommended_date,recommended_price,target1,target2,target3,ROI)
      if target_point == 1:
        message_for_target1(stock_name,recommended_date,recommended_price,target1,target2,target3,ROI)
      change_flag_status(worksheet,row_number,f"{flag_status}")
      st.write("\n messege sent \n\n")

def main():
    st.title("Stocks alert check")

    if st.button("Refresh", type='primary'):
        st.write("Reading Gsheet..... ")

        df, worksheet = read_gsheet(credentials_path)
        st.dataframe(df)
        targer3_status_chk_df=df[df['Flag'] == '2']
        targer2_status_chk_df=df[df['Flag'] == '1']
        targer1_status_chk_df=df[df['Flag'] == '' ]
        
        ########### checking when 2 target is already achived ###########
        if not targer3_status_chk_df.empty: # check for target  3 is achived or not
            target3_achive_df=targer3_status_chk_df[(targer3_status_chk_df['Status3']=='Achieved') & (targer3_status_chk_df['Flag']=='2')]
            target_point = 3
            flag_status = "succeed"
            st.write("checking for 2 target already achived")
            sub_process(target3_achive_df,worksheet,target_point,flag_status)

        
        ########### checking when 1 target is already achived ###########
        if not targer2_status_chk_df.empty: # check for target  2 is achived or not
            target_3_df = targer2_status_chk_df[(targer2_status_chk_df['Status2']=='Achieved') & (targer2_status_chk_df['Status3']=='Achieved') & (targer2_status_chk_df['Flag']!='2')]
            target_2_df = targer2_status_chk_df[(targer2_status_chk_df['Status2']=='Achieved') & (targer2_status_chk_df['Status3']!='Achieved') & (targer2_status_chk_df['Flag']!='2')]
            st.write("checking for 1 target already achived")
            if not target_3_df.empty:
                target_point = 3
                flag_status = "succeed"
                sub_process(target_3_df,worksheet,target_point,flag_status)
            if not target_2_df.empty:
                target_point = 2
                flag_status = "2"
                sub_process(target_2_df,worksheet,target_point,flag_status)

        ########### checking when no target is achived ###########
        if not targer1_status_chk_df.empty: # check for target  1 is achived or not
            target_3_df =targer1_status_chk_df[(targer1_status_chk_df['Status1']=='Achieved') & (targer1_status_chk_df['Status2']=='Achieved') & (targer1_status_chk_df['Status3']=='Achieved')]
            target_2_df = targer1_status_chk_df[(targer1_status_chk_df['Status1']=='Achieved') & (targer1_status_chk_df['Status2']=='Achieved') & (targer1_status_chk_df['Status3']!='Achieved')]
            target_1_df = targer1_status_chk_df[(targer1_status_chk_df['Status1']=='Achieved') & (targer1_status_chk_df['Status2']!='Achieved') & (targer1_status_chk_df['Status3']!='Achieved')]
            st.write("checking for no target achived")
            if not target_3_df.empty:
                target_point = 3
                flag_status = "succeed"
                sub_process(target_3_df,worksheet,target_point,flag_status)
            if not target_2_df.empty:
                target_point = 2
                flag_status = "2"
                sub_process(target_2_df,worksheet,target_point,flag_status)
            if not target_1_df.empty:
                target_point = 1
                flag_status = "1"
                sub_process(target_1_df,worksheet,target_point,flag_status)
            
            ########### When Stoploss hit  ###########
            Stoploss_df=targer1_status_chk_df[(targer1_status_chk_df['Status4']=='Stoploss') & (targer1_status_chk_df['Flag']!='-1')]
            if not Stoploss_df.empty:
                for row in range(len(Stoploss_df)):
                    stock_name = Stoploss_df["Stock Name"].iloc[row]
                    recommended_date = Stoploss_df["Recommendation Date"].iloc[row]
                    recommended_price = Stoploss_df["Recommended Price"].iloc[row]
                    Stoploss1 = Stoploss_df["Stoploss"].iloc[row]
                    LII = str(round(((float(Stoploss_df["Recommended Price"].iloc[row])-float(Stoploss_df["Stoploss"].iloc[row]))/float(Stoploss_df["Recommended Price"].iloc[row]))*100,2))
                    row_number = Stoploss_df.index[row]
                    print(Stoploss_df.index[row])
                    message_for_telegram_for_stoploss = f"""*{stock_name.upper()}* stock recommend to our premium group members. 
                    On *{recommended_date}* at price *{recommended_price}*
                    SL - *{Stoploss1}* Hit
                    *{LII}%* lose.❌ """
                    response = send_message(message_for_telegram_for_stoploss)
                    st.write(message_for_telegram_for_stoploss)
                    st.write(response)
                    change_flag_status(worksheet,row_number,"-1")


    
        
    
if __name__ == "__main__":
    main()