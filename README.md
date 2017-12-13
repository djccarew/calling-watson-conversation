# Calling Watson Conversation - Adding a telephoine voice interface to your chatbot with Discovery 

This application demonstrates how you can add a telephone voice interface to a chatbot developed  with the [Watson Conversation Service](https://console.bluemix.net/docs/services/conversation/index.html#about). The telephone voice interface is handled by [Nexmo](https://www.nexmo.com/about-nexmo) a third pary service available in the  IBM Cloud . Since the Watson Converation service only recognizes text input and only generates text output,  we also utilize  [Watson Speech to Text service](https://console.bluemix.net/docs/services/speech-to-text/getting-started.html) and [Watson Text to Speech service](https://console.bluemix.net/docs/services/text-to-speech/getting-started.html) to go between the text data needed to interface with the Conversation service and and the voice data needed to interface with Nexmo and the person calling your chatbot.

Acknowledgements: This application extends the Nexmo sample [Real-time Call Transcription Using IBM Watson and Python](https://www.nexmo.com/blog/2017/10/03/real-time-call-transcription-ibm-watson-python-dr/). Many thanks to Sam Manchin of Nexmo for providing this. 

## How the app works

Here’s an overview of how  it all works. 

<img src="readme_images/switch_config.png" width="550"></img>

As shown in the diagram, you link your Nexmo number to an instance of this application that receives the voice data from an  incoming phone call . The app calls Watson Speech to Text to convert the voice data to text and then sends that text as input to a chatbot powered by a Watson Conversation workspace.  The reply from  the chatbot is  then sent to Watson Text to Speech and the resulting voice data is sent back to the caller connected to your virtual number . 


## Deploy to IBM Cloud
[![Deploy to Bluemix](https://metrics-tracker.mybluemix.net/stats/527357940ca5e1027fbf945add3b15c4/button.svg)](https://bluemix.net/deploy?repository=https://github.com/djccarew/calling-watson-conversation.git)

## Getting Started locally

<img src="readme_images/deploy-locally.png"></img>

### Before you begin

-  Ensure that you have a [Bluemix account](https://console.ng.bluemix.net/registration/). While you can deply the app locally, you must still use Bluemix for the Watson services.
-  Ensure that you have [a Nexmo account](https://dashboard.nexmo.com/sign-up). Make sure to go through the verification process to complete the sign up. You will be called or sent a text with an activation code that you must enter to complete the signup. You will get a free account with a &euro;2 credit which is more than enough to get this app up and running. To keep going beyond that  you can add credit to your Nexmo account in &euro;10 euro increments (about $12 USD).
- To run the app locally you will need to install [ngrok] (https://ngrok.com/download) which will give the app running on your local machine a public url that can be used by Nexmo to interact with your app. If you run the app in Bluemix ngrok is not required.



### Create the services

1. In Bluemix, [create a Conversation Service instance](https://console.ng.bluemix.net/registration/?target=/catalog/services/conversation/).
  

2. In Bluemix, [create a Speech to Text Service instance](https://console.ng.bluemix.net/registration/?target=/catalog/services/speech-to-text/).
  
3. In Bluemix, [create a Text to Speech Service instance](https://console.ng.bluemix.net/registration/?target=/catalog/services/text-to-speech/).
  
### Get Conversation Workspace ID

In order for this app to interact with your Watson Conversation workspace you  need to configure it with the unique  Workspace ID.  The Conversation service will have a sample workspace already created (Car Demo) so you can use that if you don't have another workspace to work with. If you're new to Watson Conversation, note that a workspace is a container for all the artifacts that define the behavior of your service (ie: intents, entities and chat flows). 

For more information on workspaces, see the full  [Conversation service documentation](https://console.bluemix.net/docs/services/conversation/configure-workspace.html#configuring-a-conversation-workspace).

1. Navigate to the Bluemix dashboard and select the **Conversation** service you created.

  ![](readme_images/workspace_dashboard.png)

2. Click the **Launch Tool** button under the **Manage** tab. This opens a new tab in your browser, where you are prompted to login if you have not done so before. Use your Bluemix credentials.

  ![](readme_images/workspace_launch.png)

3. Refresh your browser. A new workspace tile is created within the tooling. Select the _menu_ button within the workspace tile, then select **View details**:

  ![Workpsace Details](readme_images/details.PNG)

  <a name="workspaceID">
  In the Details UI, copy the 36 character UNID **ID** field. This is the **Workspace ID**.
  </a>

  ![](readme_images/workspaceid.PNG)


### Building locally

To build the application:

1. Clone the repository  
   ```
   git clone https://github.com/watson-developer-cloud/conversation-with-discovery
   ```

2. Navigate to the `conversation-with-discovery` folder

3. For Windows, type `gradlew.bat build`. Otherwise, type `./gradlew build`.

4. The built WAR file (conversation-with-discovery-0.1-SNAPSHOT.war) is in the `conversation-with-discovery/build/libs/` folder.

### Running locally

1. Copy the WAR file generated above into the Liberty install directory's dropins folder. For example, `<liberty install directory>/usr/servers/<server profile>/dropins`.  
2. Navigate to the `conversation-with-discovery/src/main/resources` folder. Copy the `server.env` file.  
3. Navigate to the `<liberty install directory>/usr/servers/<server name>/` folder (where < server name > is the name of the Liberty server you wish to use). Paste the `server.env` here.  
4. In the `server.env` file, in the **"conversation"** section.  
  - Populate the "password" field.
  - Populate the "username" field.
  - Add the **WORKSPACE_ID** that you [copied earlier](#workspaceID).  
5. In the `server.env` file, in the **"discovery"** section.  
  - Populate the "password" field.
  - Populate the "username" field.
  - Add the **COLLECTION_ID** and **ENVIRONMENT_ID** that you [copied from the Discovery UI](#environmentID) 
  - (Optional) Edit the **DISCOVERY_QUERY_FIELDS** field if you set up a custom configuration . [Learn more here](custom_config/config_instructions.md).
6. Start the server using Eclipse or CLI with the command `server run <server name>` (use the name you gave your server). If you are using a Unix command line, first navigate to the `<liberty install directory>/bin/` folder and then `./server run <server name>`.
7. Liberty notifies you when the server starts and includes the port information.  
8. Open your browser of choice and go to the URL displayed in Step 6. By default, this is `http://localhost:9080/`.

---

<a name="ingestion">
</a>

### Create a collection and ingest documents in Discovery

1. Navigate to your Discovery instance in your Bluemix dashboard
2. Launch the Discovery tooling  
  ![](readme_images/discovery_tooling.png)

3. Create a new data collection, name it whatever you like, and select the default configuration.
  <div style="text-align:center;"><img src='readme_images/discovery_collection.png'></div><br>

  - After you're done, there should be a new private collection in the UI  
  <div style="text-align:center;"><img src='readme_images/ford_collection.png'></div>


4. (Optional) [Set up the custom configuration](custom_config/config_instructions.md) in order to enrich specific Discovery fields and improve results

5. On the collection tooling interface, click "Switch" on the Configuration line and select your new configuration

  <img src="readme_images/switch_config.png" width="550"></img>

6. Download and unzip the [manualdocs.zip](src/main/resources/manualdocs.zip) in this repo to reveal a set of JSON documents

7. In the tooling interface, drag and drop (or browse and select) all of the JSON files into the "Add data to this collection" box
  - This may take a few minutes -- you will see a notification when the process is finished

<a name="credentials">
</a>

### Service Credentials

1. Go to the Bluemix Dashboard and select the Conversation/Discovery service instance. Once there, select the **Service Credentials** menu item.

  <img src="readme_images/credentials.PNG" width="500"></img>

2. Select **New Credential**. Name your credentials then select **Add**.

3. Copy the credentials (or remember this location) for later use.

<a name="workspace">
</a>

### Import a workspace

To use the app you're creating, you need to add a workspace to your Conversation service. A workspace is a container for all the artifacts that define the behavior of your service (ie: intents, entities and chat flows). For this sample app, a workspace is provided.

For more information on workspaces, see the full  [Conversation service documentation](https://console.bluemix.net/docs/services/conversation/configure-workspace.html#configuring-a-conversation-workspace).

1. Navigate to the Bluemix dashboard and select the **Conversation** service you created.

  ![](readme_images/workspace_dashboard.png)

2. Click the **Launch Tool** button under the **Manage** tab. This opens a new tab in your browser, where you are prompted to login if you have not done so before. Use your Bluemix credentials.

  ![](readme_images/workspace_launch.png)

3. Download the [exported JSON file](src/main/resources/workspace.json) that contains the Workspace contents.

4. Select the import icon: ![](readme_images/importGA.PNG). Browse to (or drag and drop) the JSON file that you downloaded in Step 3. Choose to import **Everything(Intents, Entities, and Dialog)**. Then select **Import** to finish importing the workspace.

5. Select the _menu_ button within the workspace tile for the Card Demo, then select **View details**:

  ![Workpsace Details](readme_images/details.PNG)

  <a name="workspaceID">
  In the Details UI, copy the 36 character UNID **ID** field. This is the **Workspace ID**. Paste it into a text file for later use
  </a>

  ![](readme_images/workspaceid.PNG)


### Adding environment variables in Bluemix

1. In Bluemix, open the application from the Dashboard. Select **Runtime** and then **Environment Variables**.
  ![](readme_images/env_var_tab.png)
2. In the **User Defined** section, add the following Conversations environment variables:
  - **CONVERSATION_PASSWORD**: Use your Conversations [service credentials](#credentials)
  - **CONVERSATION_USERNAME**: Use your Conversations service credentials
  - **WORKSPACE_ID**: Add the Workspace ID you [copied earlier](#workspaceID).
3. Then add the following four Discovery environment variables to this section:
  - **DISCOVERY_PASSWORD**: Use your Discovery [service credentials](#credentials)
  - **DISCOVERY_USERNAME**: Use your Discovery service credentials
  - **DISCOVERY_COLLECTION_ID**: Find your collection ID in the Discovery collection you created
  - **DISCOVERY_ENVIRONMENT_ID**: Find your environment ID in the Discovery collection you created
  - **DISCOVERY_QUERY_FIELDS**: Set this value to 'none'. If you set up a custom configuration (optional), set this value to the name of your enrichment fields, separated by commas. [Learn more here.](custom_config/config_instructions.md).
  ![](readme_images/env_var_text.png)
4. Select **SAVE**.
5. Restart your application.

---

### Troubleshooting in Bluemix

1. Log in to Bluemix, you'll be taken to the dashboard.
1. Navigate to the the application you previously created.
1. Select **Logs**.  
  ![](readme_images/logs_new.png)

## License

  This sample code is licensed under Apache 2.0.
  Full license text is available in [LICENSE](LICENSE).

## Contributing

  See [CONTRIBUTING](CONTRIBUTING.md).

## Open Source @ IBM

  Find more open source projects on the
  [IBM Github Page](http://ibm.github.io/).



[cloud_foundry]: https://github.com/cloudfoundry/cli
[getting_started]: https://www.ibm.com/watson/developercloud/doc/common/
[conversation]: http://www.ibm.com/watson/developercloud/conversation.html
[discovery]: http://www.ibm.com/watson/developercloud/discovery.html

[docs]: http://www.ibm.com/watson/developercloud/conversation/
[sign_up]: https://console.ng.bluemix.net/registration/
