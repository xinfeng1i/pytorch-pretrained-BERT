# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors.
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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import shutil
import pytest

from pytorch_pretrained_bert import (XLMConfig, XLMModel, XLMForQuestionAnswering, XLMForSequenceClassification)
from pytorch_pretrained_bert.modeling_xlm import PRETRAINED_MODEL_ARCHIVE_MAP

from .model_tests_commons import (create_and_check_commons, ConfigTester, ids_tensor)


class XLMModelTest(unittest.TestCase):
    class XLMModelTester(object):

        def __init__(self,
                     parent,
                     batch_size=13,
                     seq_length=7,
                     is_training=True,
                     use_input_lengths=True,
                     use_token_type_ids=True,
                     use_labels=True,
                     gelu_activation=True,
                     sinusoidal_embeddings=False,
                     causal=False,
                     asm=False,
                     n_langs=2,
                     vocab_size=99,
                     n_special=0,
                     hidden_size=32,
                     num_hidden_layers=5,
                     num_attention_heads=4,
                     hidden_dropout_prob=0.1,
                     attention_probs_dropout_prob=0.1,
                     max_position_embeddings=512,
                     type_vocab_size=16,
                     type_sequence_label_size=2,
                     initializer_range=0.02,
                     num_labels=3,
                     num_choices=4,
                     summary_type="last",
                     use_proj=True,
                     scope=None,
                     all_model_classes = (XLMModel,),  # , XLMForSequenceClassification, XLMForTokenClassification),
                    ):
            self.parent = parent
            self.batch_size = batch_size
            self.seq_length = seq_length
            self.is_training = is_training
            self.use_input_lengths = use_input_lengths
            self.use_token_type_ids = use_token_type_ids
            self.use_labels = use_labels
            self.gelu_activation = gelu_activation
            self.sinusoidal_embeddings = sinusoidal_embeddings
            self.asm = asm
            self.n_langs = n_langs
            self.vocab_size = vocab_size
            self.n_special = n_special
            self.summary_type = summary_type
            self.causal = causal
            self.use_proj = use_proj
            self.hidden_size = hidden_size
            self.num_hidden_layers = num_hidden_layers
            self.num_attention_heads = num_attention_heads
            self.hidden_dropout_prob = hidden_dropout_prob
            self.attention_probs_dropout_prob = attention_probs_dropout_prob
            self.max_position_embeddings = max_position_embeddings
            self.n_langs = n_langs
            self.type_sequence_label_size = type_sequence_label_size
            self.initializer_range = initializer_range
            self.summary_type = summary_type
            self.num_labels = num_labels
            self.num_choices = num_choices
            self.scope = scope
            self.all_model_classes = all_model_classes

        def prepare_config_and_inputs(self):
            input_ids = ids_tensor([self.batch_size, self.seq_length], self.vocab_size)

            input_lengths = None
            if self.use_input_lengths:
                input_lengths = ids_tensor([self.batch_size], vocab_size=self.seq_length-1)

            token_type_ids = None
            if self.use_token_type_ids:
                token_type_ids = ids_tensor([self.batch_size, self.seq_length], self.n_langs)

            sequence_labels = None
            token_labels = None
            choice_labels = None
            if self.use_labels:
                sequence_labels = ids_tensor([self.batch_size], self.type_sequence_label_size)
                token_labels = ids_tensor([self.batch_size, self.seq_length], self.num_labels)
                choice_labels = ids_tensor([self.batch_size], self.num_choices)

            config = XLMConfig(
                 vocab_size_or_config_json_file=self.vocab_size,
                 n_special=self.n_special,
                 emb_dim=self.hidden_size,
                 n_layers=self.num_hidden_layers,
                 n_heads=self.num_attention_heads,
                 dropout=self.hidden_dropout_prob,
                 attention_dropout=self.attention_probs_dropout_prob,
                 gelu_activation=self.gelu_activation,
                 sinusoidal_embeddings=self.sinusoidal_embeddings,
                 asm=self.asm,
                 causal=self.causal,
                 n_langs=self.n_langs,
                 max_position_embeddings=self.max_position_embeddings,
                 initializer_range=self.initializer_range,
                 summary_type=self.summary_type,
                 use_proj=self.use_proj)

            return config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels

        def check_loss_output(self, result):
            self.parent.assertListEqual(
                list(result["loss"].size()),
                [])

        def create_and_check_xlm_model(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
            model = XLMModel(config=config)
            model.eval()
            outputs = model(input_ids, lengths=input_lengths, langs=token_type_ids)
            sequence_output = outputs[0]
            result = {
                "sequence_output": sequence_output,
            }
            self.parent.assertListEqual(
                list(result["sequence_output"].size()),
                [self.batch_size, self.seq_length, self.hidden_size])


        # def create_and_check_xlm_for_masked_lm(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
        #     model = XLMForMaskedLM(config=config)
        #     model.eval()
        #     loss, prediction_scores = model(input_ids, token_type_ids, input_lengths, token_labels)
        #     result = {
        #         "loss": loss,
        #         "prediction_scores": prediction_scores,
        #     }
        #     self.parent.assertListEqual(
        #         list(result["prediction_scores"].size()),
        #         [self.batch_size, self.seq_length, self.vocab_size])
        #     self.check_loss_output(result)


        # def create_and_check_xlm_for_question_answering(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
        #     model = XLMForQuestionAnswering(config=config)
        #     model.eval()
        #     loss, start_logits, end_logits = model(input_ids, token_type_ids, input_lengths, sequence_labels, sequence_labels)
        #     result = {
        #         "loss": loss,
        #         "start_logits": start_logits,
        #         "end_logits": end_logits,
        #     }
        #     self.parent.assertListEqual(
        #         list(result["start_logits"].size()),
        #         [self.batch_size, self.seq_length])
        #     self.parent.assertListEqual(
        #         list(result["end_logits"].size()),
        #         [self.batch_size, self.seq_length])
        #     self.check_loss_output(result)


        # def create_and_check_xlm_for_sequence_classification(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
        #     config.num_labels = self.num_labels
        #     model = XLMForSequenceClassification(config)
        #     model.eval()
        #     loss, logits = model(input_ids, token_type_ids, input_lengths, sequence_labels)
        #     result = {
        #         "loss": loss,
        #         "logits": logits,
        #     }
        #     self.parent.assertListEqual(
        #         list(result["logits"].size()),
        #         [self.batch_size, self.num_labels])
        #     self.check_loss_output(result)


        # def create_and_check_xlm_for_token_classification(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
        #     config.num_labels = self.num_labels
        #     model = XLMForTokenClassification(config=config)
        #     model.eval()
        #     loss, logits = model(input_ids, token_type_ids, input_lengths, token_labels)
        #     result = {
        #         "loss": loss,
        #         "logits": logits,
        #     }
        #     self.parent.assertListEqual(
        #         list(result["logits"].size()),
        #         [self.batch_size, self.seq_length, self.num_labels])
        #     self.check_loss_output(result)


        # def create_and_check_xlm_for_multiple_choice(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
        #     config.num_choices = self.num_choices
        #     model = XLMForMultipleChoice(config=config)
        #     model.eval()
        #     multiple_choice_inputs_ids = input_ids.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
        #     multiple_choice_token_type_ids = token_type_ids.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
        #     multiple_choice_input_lengths = input_lengths.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
        #     loss, logits = model(multiple_choice_inputs_ids,
        #                  multiple_choice_token_type_ids,
        #                  multiple_choice_input_lengths,
        #                  choice_labels)
        #     result = {
        #         "loss": loss,
        #         "logits": logits,
        #     }
        #     self.parent.assertListEqual(
        #         list(result["logits"].size()),
        #         [self.batch_size, self.num_choices])
        #     self.check_loss_output(result)


        def create_and_check_xlm_commons(self, config, input_ids, token_type_ids, input_lengths, sequence_labels, token_labels, choice_labels):
            inputs_dict = {'input_ids': input_ids, 'token_type_ids': token_type_ids, 'attention_mask': input_lengths}
            create_and_check_commons(self, config, inputs_dict)

    def test_default(self):
        self.run_tester(XLMModelTest.XLMModelTester(self))

    def test_config(self):
        config_tester = ConfigTester(self, config_class=XLMConfig, emb_dim=37)
        config_tester.run_common_tests()

    @pytest.mark.slow
    def test_model_from_pretrained(self):
        cache_dir = "/tmp/pytorch_pretrained_bert_test/"
        for model_name in list(PRETRAINED_MODEL_ARCHIVE_MAP.keys())[:1]:
            model = XLMModel.from_pretrained(model_name, cache_dir=cache_dir)
            shutil.rmtree(cache_dir)
            self.assertIsNotNone(model)

    def run_tester(self, tester):
        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_xlm_model(*config_and_inputs)

        # config_and_inputs = tester.prepare_config_and_inputs()
        # tester.create_and_check_xlm_for_masked_lm(*config_and_inputs)

        # config_and_inputs = tester.prepare_config_and_inputs()
        # tester.create_and_check_xlm_for_multiple_choice(*config_and_inputs)

        # config_and_inputs = tester.prepare_config_and_inputs()
        # tester.create_and_check_xlm_for_question_answering(*config_and_inputs)

        # config_and_inputs = tester.prepare_config_and_inputs()
        # tester.create_and_check_xlm_for_sequence_classification(*config_and_inputs)

        # config_and_inputs = tester.prepare_config_and_inputs()
        # tester.create_and_check_xlm_for_token_classification(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_xlm_commons(*config_and_inputs)

if __name__ == "__main__":
    unittest.main()