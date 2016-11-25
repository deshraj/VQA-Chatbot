# VQA Chatbot

A Chatbot based on Visual Question Answering(VQA)


## How to setup on local machine

1. Setting up VQA Chatbot on your local system is really easy. Follow the following steps:

    ```shell
    git clone https://github.com/deshraj/vqa_chatbot.git
    cd vqa_chatbot
    virtualenv env
    source env/bin/activate
    pip install -requirements.txt
    ```

2. Install pytorch using following commands:

    ```shell
    git clone https://github.com/hughperkins/pytorch.git
    cd pytorch
    source ~/torch/install/bin/torch-activate
    ./build.sh
    ```

3. Run the local django server using following command:

    ```shell
    python manage.py runserver
    ```

4. Open new terminal window to run the RabbitMQ worker and run the following command:

    ```shell
    source env/bin/activate
    python worker.py
    ```

Now, you are good to go. Visit http://127.0.0.1:8000

## Interested in contributing

If you want to contribute to the project, then fork the repository and work on feature branch and create pull requests. If you find some issues, please open issues. 
