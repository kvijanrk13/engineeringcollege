# dashboard/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
import os
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db.models import Q