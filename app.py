import boto3
import botocore.config
import json
from datetime import datetime

def blog_generation_using_bedrock(blogTopic:str)->str:
    prompt = f"""<s>[INST]Human: write a 300 words blog on the topic {blogTopic}
    Assistant:[/INST]
    """
    
    body = {
        "prompt" : prompt,
        "max_gen_len": 512,
        "temperature": 0.2,
        "top_p" : 0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name = "us-east-1",
                               config = botocore.config.Config(read_timeout = 300 , retries={'max_attempts':3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="us.meta.llama3-2-1b-instruct-v1:0")

        # response_content = response.get('body').read()
        response_data = json.loads(response["body"].read())
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""
    
def save_blog_detail_in_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket = s3_bucket,Key = s3_key, Body = generate_blog)
        print("Blog saved to S3")
    except Exception as e:
        print("Error when saving the blog to s3")


def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blogTopic = event['blog_topic']
    generate_blog =  blog_generation_using_bedrock(blogTopic=blogTopic)

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = "bloggeneration"
        save_blog_detail_in_s3(s3_key,s3_bucket,generate_blog)


    else:
        print("No blog was generated")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Topic: {blogTopic} \n {generate_blog}')
    }