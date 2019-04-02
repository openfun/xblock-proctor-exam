#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.
    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(name="xblock-proctor-exam",
      version="0.8.1-alpha",
      description="Xblock restricting access to course test to Proctor Exam monitoring process",
      author="Open FUN (France Universite Numérique)",
      author_email="fun.dev@fun-mooc.fr",
      license="AGPL 3.0",
      url="https://github.com/openfun/xblock-proctor-exam",
      platforms=["any"],
      packages=[
        "proctor_exam",
      ],
    install_requires=[
        "XBlock",
        "XBlock-utils",
        "configurable-lti-consumer-xblock"
    ],
    entry_points={
        'xblock.v1': [
            'proctor_exam = proctor_exam:ProctorExamXBlock',
        ]
    },
    package_data=package_data("proctor_exam", [
          "static",
          "public",
          "locale"
          ]
    ),
)
