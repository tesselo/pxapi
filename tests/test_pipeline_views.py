import tempfile
import zipfile

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse


class PipelineViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.usr = User.objects.create_user(
            username="michael", email="michael@bluth.com", password="bananastand"
        )
        self.client.login(username="michael", password="bananastand")

    def test_trainingdata(self):
        zip = tempfile.NamedTemporaryFile(suffix=".zip")
        txt = tempfile.NamedTemporaryFile(suffix=".txt")
        with zipfile.ZipFile(zip.name, "w") as fl:
            fl.write(txt.name, compress_type=zipfile.ZIP_DEFLATED)
        response = self.client.post(
            reverse("trainingdata-list"),
            data={
                "name": "Bananastand",
                "zipfile": zip,
                "reference_date": "2021-01-01",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = response.json()
        self.assertEqual(response["name"], "Bananastand")
        self.assertEqual(response["batchjob_parse"]["status"], "UNKNOWN")
        self.assertEqual(response["reference_date"], "2021-01-01")
