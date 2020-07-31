# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test for ImageFolder."""

import os
import mock

from tensorflow_datasets.core.folder_dataset import image_folder
import tensorflow_datasets.public_api as tfds

_EXAMPLE_DIR = os.path.join(
    tfds.testing.test_utils.fake_examples_dir(), 'image_folder')

original_init = tfds.ImageFolder.__init__
original_download_and_prepare = tfds.ImageFolder.download_and_prepare


def new_init(self, root_dir=None, **kwargs):
  assert root_dir is None
  del kwargs
  original_init(self, root_dir=_EXAMPLE_DIR)


class ImageFolderTest(tfds.testing.DatasetBuilderTestCase):
  """Test for ImageFolder."""

  DATASET_CLASS = tfds.ImageFolder
  SPLITS = {
      'train': 2,
      'test': 6,
  }

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    super(ImageFolderTest, cls).setUpClass()
    cls.DATASET_CLASS.__init__ = new_init
    cls.DATASET_CLASS.download_and_prepare = mock.Mock(return_value=None)

  @classmethod
  def tearDownClass(cls):
    super().tearDownClass()
    cls.DATASET_CLASS.__init__ = original_init
    cls.DATASET_CLASS.download_and_prepare = original_download_and_prepare

  def test_registered(self):
    # Custom datasets shouldn't be registered
    self.assertNotIn(tfds.ImageFolder.name, tfds.list_builders())


class ImageFolderFunctionTest(tfds.testing.TestCase):
  """Tests for ImageFolder functions."""

  def test_properties(self):
    images = [
        'root_dir/train/label1/img1.png',
        'root_dir/train/label3/img3.png',
        'root_dir/train/label3/img1.png',
        'root_dir/train/label3/img2.png',
        'root_dir/train/label2/img1.png',
        'root_dir/train/label2/img2.png',

        'root_dir/val/label1/img1.png',
        'root_dir/val/label2/img2.png',

        'root_dir/test/label1/img1.png',
        'root_dir/test/label2/img1.png',
        'root_dir/test/label4/img1.PNG',
        'root_dir/test/label4/unsuported.txt',
    ]

    with tfds.testing.MockFs() as fs:
      for file in images:
        fs.add_file(file)

      split_examples, labels = image_folder._get_split_label_images('root_dir')
      builder = tfds.ImageFolder(root_dir='root_dir')

    self.assertEqual(split_examples, {
        'train': [
            image_folder._Example(
                image_path='root_dir/train/label2/img1.png', label='label2'),
            image_folder._Example(
                image_path='root_dir/train/label3/img3.png', label='label3'),
            image_folder._Example(
                image_path='root_dir/train/label3/img2.png', label='label3'),
            image_folder._Example(
                image_path='root_dir/train/label3/img1.png', label='label3'),
            image_folder._Example(
                image_path='root_dir/train/label2/img2.png', label='label2'),
            image_folder._Example(
                image_path='root_dir/train/label1/img1.png', label='label1'),
        ],
        'val': [
            image_folder._Example(
                image_path='root_dir/val/label2/img2.png', label='label2'),
            image_folder._Example(
                image_path='root_dir/val/label1/img1.png', label='label1'),
        ],
        'test': [
            image_folder._Example(
                image_path='root_dir/test/label1/img1.png', label='label1'),
            image_folder._Example(
                image_path='root_dir/test/label2/img1.png', label='label2'),
            image_folder._Example(
                image_path='root_dir/test/label4/img1.PNG', label='label4'),
        ],
    })
    self.assertEqual(builder.info.splits['train'].num_examples, 6)
    self.assertEqual(builder.info.splits['val'].num_examples, 2)
    self.assertEqual(builder.info.splits['test'].num_examples, 3)

    expected_labels = [
        'label1',
        'label2',
        'label3',
        'label4',
    ]
    self.assertEqual(expected_labels, labels)
    self.assertEqual(builder.info.features['label'].names, expected_labels)


if __name__ == '__main__':
  tfds.testing.test_main()
