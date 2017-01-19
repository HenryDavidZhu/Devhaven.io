#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.contrib import auth
from hitcount.views import HitCountDetailView
import sys

# Create your models here.

class User(models.Model):

    errors = {'required': '', 'invalid': 'Enter a valid value'}
    username = models.CharField(max_length=30, blank=False, null=True,
                                error_messages=errors)
    email = models.EmailField()
    password = models.CharField(max_length=60, blank=False, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.username


class Post(models.Model):

    title = models.TextField(max_length=150)
    slug = models.SlugField(max_length=255)
    text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('auth.User', null=True, blank=True)
    commentCount = 0
    reportlink = ""

    CHOICES = [
        ('Hardware and OS', 'Hardware and OS'),
        ('Desktops', 'Desktops'),
        ('Tablets', 'Tablets'),
        ('Phones', 'Phones'),
        ('Wearables', 'Wearables'),
        ('Windows', 'Windows'),
        ('Mac OS X', 'Mac OS X'),
        ('Linux and Unix', 'Linux and Unix'),
        ('Programming and Computer Science',
         'Programming and Computer Science'),
        ('Software Development', 'Software Development'),
        ('Web Development (Front)', 'Web Development (Front)'),
        ('Web Development (Back)', 'Web Development (Back)'),
        ('Mobile Development', 'Mobile Development'),
        ('Game Development', 'Game Development'),
        ('Algorithms and Data Structures',
         'Algorithms and Data Structures'),
        ('Databases', 'Databases'),
        ('IDE / Text Editors', 'IDE / Text Editors'),
        ('Community Discussion', 'Community Discussion'),
        ('Tutorial', 'Tutorial'),
        ('Opinion', 'Opinion'),
        ('Miscellaneous', 'Miscellaneous'),
        ]
    field = models.CharField(choices=CHOICES, max_length=200)

    def __unicode__(self):
        return self.title.encode('utf-8')

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('blog_post_detail', (), {'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):

    name = models.ForeignKey('auth.User', null=True, blank=True)
    text = models.TextField()
    post = models.ForeignKey(Post)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text


class SearchTerm(models.Model):

    CHOICES = [
        ('all', 'all'),
        ('Hardware and OS', 'Hardware and OS'),
        ('Desktops', 'Desktops'),
        ('Tablets', 'Tablets'),
        ('Phones', 'Phones'),
        ('Wearables', 'Wearables'),
        ('Windows', 'Windows'),
        ('Mac OS X', 'Mac OS X'),
        ('Linux and Unix', 'Linux and Unix'),
        ('Programming and Computer Science',
         'Programming and Computer Science'),
        ('Software Development', 'Software Development'),
        ('Web Development (Front)', 'Web Development (Front)'),
        ('Web Development (Back)', 'Web Development (Back)'),
        ('Mobile Development', 'Mobile Development'),
        ('Game Development', 'Game Development'),
        ('Algorithms and Data Structures',
         'Algorithms and Data Structures'),
        ('Databases', 'Databases'),
        ('IDE / Text Editors', 'IDE / Text Editors'),
        ('Community Discussion', 'Community Discussion'),
        ('Tutorial', 'Tutorial'),
        ('Opinion', 'Opinion'),
        ('Miscellaneous', 'Miscellaneous'),
        ]
    category = models.CharField(choices=CHOICES, max_length=200)