import bcrypt, requests
from PIL import Image, ImageOps
from io import BytesIO
import numpy as np
import time
from PIL import Image
from collections import Counter


def get_anilist_activity(activity_id):
    query = """
    query ($id: Int!) {
  Activity(id: $id) {
    ... on TextActivity {
    userId
    }
  }
}
    """

    # Define our query variables and values that will be used in the query request
    variables = {"id": activity_id}

    url = "https://graphql.anilist.co"

    # Make the HTTP Api request
    response = requests.post(url, json={"query": query, "variables": variables})
    print(response.json())
    return response.json()
