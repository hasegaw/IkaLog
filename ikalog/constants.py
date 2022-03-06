#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from ikalog.utils import statink_json

#  IkaLog Constants

stages = {
    'anchovy': {'ja': 'アンチョビットゲームズ', 'en': 'Ancho-V Games'},
    'arowana':  {'ja': 'アロワナモール',      'en': 'Arowana Mall'},
    'bbass':    {'ja': 'Bバスパーク',         'en': 'Blackbelly Skatepark'},
    'dekaline': {'ja': 'デカライン高架下',    'en': 'Urchin Underpass'},
    'hakofugu': {'ja': 'ハコフグ倉庫',        'en': 'Walleye Warehouse', },
    'hirame':   {'ja': 'ヒラメが丘団地',      'en': 'Flounder Heights', },
    'hokke':    {'ja': 'ホッケふ頭',          'en': 'Port Mackerel'},
    'kinmedai': {'ja': 'キンメダイ美術館',    'en': 'Museum d\'Alfonsino'},
    'mahimahi': {'ja': 'マヒマヒリゾート&スパ', 'en': 'Mahi-Mahi Resort', },
    'masaba':   {'ja': 'マサバ海峡大橋',      'en': 'Hammerhead Bridge', },
    'mongara':  {'ja': 'モンガラキャンプ場',  'en': 'Camp Triggerfish', },
    'mozuku':   {'ja':  'モズク農園',         'en': 'Kelp Dome', },
    'negitoro': {'ja': 'ネギトロ炭鉱',        'en': 'Bluefin Depot', },
    'shionome': {'ja': 'シオノメ油田',        'en': 'Saltspray Rig', },
    'shottsuru': {'ja': 'ショッツル鉱山',     'en': 'Piranha Pit'},
    'tachiuo':  {'ja':  'タチウオパーキング', 'en':  'Moray Towers', },
}

modes_v2 = {
    'nawabari': {'ja': 'ナワバリバトル', 'en': 'Turf War', },
    'area': {'ja': 'ガチエリア', 'en': 'Splat Zones', },
    'yagura': {'ja': 'ガチヤグラ', 'en': 'Tower Control', },
    'hoko': {'ja': 'ガチホコバトル', 'en': 'Rainmaker', },
    'asari': {'ja': 'ガチアサリ', 'en': 'Clam Blitz', },
}
rules = modes_v2 # backward compatiblity

weapons = {
    '52gal': {'ja': '.52ガロン', 'en': '.52 Gal'},
    '52gal_deco': {'ja': '.52ガロンデコ', 'en': '.52 Gal Deco'},
    '96gal': {'ja': '.96ガロン', 'en': '.96 Gal'},
    '96gal_deco': {'ja': '.96ガロンデコ', 'en': '.96 Gal Deco'},
    'bold': {'ja': 'ボールドマーカー', 'en': 'Sploosh-o-matic'},
    'bold_7': {'ja': 'ボールドマーカー7', 'en': 'Sploosh-o-matic 7'},
    'bold_neo': {'ja': 'ボールドマーカーネオ', 'en': 'Neo Sploosh-o-matic'},
    'dualsweeper': {'ja': 'デュアルスイーパー', 'en': 'Dual Squelcher'},
    'dualsweeper_custom': {'ja': 'デュアルスイーパーカスタム', 'en': 'Custom Dual Squelcher'},
    'h3reelgun': {'ja': 'H3リールガン', 'en': 'H-3 Nozzlenose'},
    'h3reelgun_cherry': {'ja': 'H3リールガンチェリー', 'en': 'Cherry H-3 Nozzlenose'},
    'h3reelgun_d': {'ja': 'H3リールガンD', 'en': 'H-3 Nozzlenose D'},
    'heroshooter_replica': {'ja': 'ヒーローシューターレプリカ', 'en': 'Hero Shot Replica'},
    'hotblaster': {'ja': 'ホットブラスター', 'en': 'Blaster'},
    'hotblaster_custom': {'ja': 'ホットブラスターカスタム', 'en': 'Custom Blaster'},
    'jetsweeper': {'ja': 'ジェットスイーパー', 'en': 'Jet Squelcher'},
    'jetsweeper_custom': {'ja': 'ジェットスイーパーカスタム', 'en': 'Custom Jet Squelcher'},
    'l3reelgun': {'ja': 'L3リールガン', 'en': 'L-3 Nozzlenose'},
    'l3reelgun_d': {'ja': 'L3リールガンD', 'en': 'L-3 Nozzlenose D'},
    'longblaster': {'ja': 'ロングブラスター', 'en': 'Range Blaster'},
    'longblaster_custom': {'ja': 'ロングブラスターカスタム', 'en': 'Custom Range laster'},
    'longblaster_necro': {'ja': 'ロングブラスターネクロ', 'en': 'Grim Range laster'},
    'momiji': {'ja': 'もみじシューター', 'en': 'Custom Splattershot Jr.'},
    'nova': {'ja': 'ノヴァブラスター', 'en': 'Luna Blaster'},
    'nova_neo': {'ja': 'ノヴァブラスターネオ', 'en': 'Luna Blaster Neo'},
    'nzap83': {'ja': 'N-ZAP83', 'en': 'N-ZAP \'83'},
    'nzap85': {'ja': 'N-ZAP85', 'en': 'N-ZAP \'85'},
    'nzap89': {'ja': 'N-ZAP89', 'en': 'N-Zap \'89'},
    'octoshooter_replica': {'ja': 'オクタシューターレプリカ', 'en': 'Octoshot Replica'},
    'prime': {'ja': 'プライムシューター', 'en': 'Splattershot Pro'},
    'prime_berry': {'ja': 'プライムシューターベリー', 'en': 'Berry Splattershot Pro'},
    'prime_collabo': {'ja': 'プライムシューターコラボ', 'en': 'Forge Splattershot Pro'},
    'promodeler_mg': {'ja': 'プロモデラーMG', 'en': 'Aerospray MG'},
    'promodeler_pg': {'ja': 'プロモデラーPG', 'en': 'Aerospray PG'},
    'promodeler_rg': {'ja': 'プロモデラーRG', 'en': 'Aerospray RG'},
    'rapid': {'ja': 'ラピッドブラスター', 'en': 'Rapid Blaster'},
    'rapid_deco': {'ja': 'ラピッドブラスターデコ', 'en': 'Rapid Blaster Deco'},
    'rapid_elite': {'ja': 'Rブラスターエリート', 'en': 'Rapid Blaster Pro'},
    'rapid_elite_deco': {'ja': 'Rブラスターエリートデコ', 'en': 'Rapid Blaster Pro Deco'},
    'sharp': {'ja': 'シャープマーカー', 'en': 'Splash-o-matic'},
    'sharp_neo': {'ja': 'シャープマーカーネオ', 'en': 'Neo Splash-o-matic'},
    'sshooter': {'ja': 'スプラシューター', 'en': 'Splattershot'},
    'sshooter_collabo': {'ja': 'スプラシューターコラボ', 'en': 'Tentatek Splattershot'},
    'sshooter_wasabi': {'ja': 'スプラシューターワサビ', 'en': 'Wasabi Splattershot'},
    'wakaba': {'ja': 'わかばシューター', 'en': 'Splattershot Jr.'},

    'carbon': {'ja': 'カーボンローラー', 'en': 'Carbon Roller'},
    'carbon_deco': {'ja': 'カーボンローラーデコ', 'en': 'Carbon Roller Deco'},
    'dynamo': {'ja': 'ダイナモローラー', 'en': 'Dynamo Roller'},
    'dynamo_burned': {'ja': 'ダイナモローラーバーンド', 'en': 'Tempered Dynamo Roller'},
    'dynamo_tesla': {'ja': 'ダイナモローラーテスラ', 'en': 'Gold Dynamo Roller'},
    'heroroller_replica': {'ja': 'ヒーローローラーレプリカ', 'en': 'Hero Roller Replica'},
    'hokusai': {'ja': 'ホクサイ', 'en': 'Octobrush'},
    'hokusai_hue': {'ja': 'ホクサイ・ヒュー', 'en': 'Octobrush Nouveau'},
    'pablo': {'ja': 'パブロ', 'en': 'Inkbrush'},
    'pablo_hue': {'ja': 'パブロ・ヒュー', 'en': 'Inkbrush Nouveau'},
    'pablo_permanent': {'ja': 'パーマネント・パブロ', 'en': 'Permanent Inkbrush'},
    'splatroller': {'ja': 'スプラローラー', 'en': 'Splat Roller'},
    'splatroller_collabo': {'ja': 'スプラローラーコラボ', 'en': 'Krak-On Splat Roller'},
    'splatroller_corocoro': {'ja': 'スプラローラーコロコロ', 'en': 'CoroCoro Splat Roller'},

    'bamboo14mk1': {'ja': '14式竹筒銃・甲', 'en': 'Bamboozler 14 MK I'},
    'bamboo14mk2': {'ja': '14式竹筒銃・乙', 'en': 'Bamboozler 14 MK II'},
    'bamboo14mk3': {'ja': '14式竹筒銃・丙', 'en': 'Bamboozler 14 Mk III'},
    'herocharger_replica': {'ja': 'ヒーローチャージャーレプリカ', 'en': 'Hero Charger Replica'},
    'liter3k': {'ja': 'リッター3K', 'en': 'E-liter 3K'},
    'liter3k_custom': {'ja': 'リッター3Kカスタム', 'en': 'Custom E-liter 3K'},
    'liter3k_scope': {'ja': '3Kスコープ', 'en': 'E-liter 3K Scope'},
    'liter3k_scope_custom': {'ja': '3Kスコープカスタム', 'en': 'Custom E-liter 3K Scope'},
    'splatcharger': {'ja': 'スプラチャージャー', 'en': 'Splat Charger'},
    'splatcharger_bento': {'ja': 'スプラチャージャーベントー', 'en': 'Bento Splat Charger'},
    'splatcharger_wakame': {'ja': 'スプラチャージャーワカメ', 'en': 'Kelp Splat Charger'},
    'splatscope': {'ja': 'スプラスコープ', 'en': 'Splatterscope'},
    'splatscope_bento': {'ja': 'スプラスコープベントー', 'en': 'Bento Splatterscope'},
    'splatscope_wakame': {'ja': 'スプラスコープワカメ', 'en': 'Kelp Splatterscope'},
    'squiclean_a': {'ja': 'スクイックリンα', 'en': 'Classic Squiffer'},
    'squiclean_b': {'ja': 'スクイックリンβ', 'en': 'New Squiffer'},
    'squiclean_g': {'ja': 'スクイックリンγ', 'en': 'Fresh Squiffer'},

    'bucketslosher': {'ja': 'バケットスロッシャー', 'en': 'Slosher'},
    'bucketslosher_deco': {'ja': 'バケットスロッシャーデコ', 'en': 'Slosher Deco'},
    'bucketslosher_soda': {'ja': 'バケットスロッシャーソーダ', 'en': 'Soda Slosher'},
    'hissen': {'ja': 'ヒッセン', 'en': 'Tri-Slosher'},
    'hissen_hue': {'ja': 'ヒッセン・ヒュー', 'en': 'Tri-Slosher Nouveau'},
    'screwslosher': {'ja': 'スクリュースロッシャー', 'en': 'Sloshing Machine'},
    'screwslosher_neo': {'ja': 'スクリュースロッシャーネオ', 'en': 'Sloshing Machine Neo'},

    'barrelspinner': {'ja': 'バレルスピナー', 'en': 'Heavy Splatling'},
    'barrelspinner_deco': {'ja': 'バレルスピナーデコ', 'en': 'Heavy Splatling Deco'},
    'barrelspinner_remix': {'ja': 'バレルスピナーリミックス', 'en': 'Heavy Splatling Remix'},
    'hydra': {'ja': 'ハイドラント', 'en': 'Hydra Splatling'},
    'hydra_custom': {'ja': 'ハイドラントカスタム', 'en': 'Custom Hydra Splatling'},
    'splatspinner': {'ja': 'スプラスピナー', 'en': 'Mini Splatling'},
    'splatspinner_collabo': {'ja': 'スプラスピナーコラボ', 'en': 'Zink Mini Splatling'},
    'splatspinner_repair': {'ja': 'スプラスピナーリペア', 'en': 'Refurbished Mini Splatling'},
}

sub_weapons = {
    'chasebomb': {'ja': 'チェイスボム', 'en':  'Seeker', },
    'jumpbeacon': {'ja': 'ジャンプビーコン', 'en':  'Squid Beakon', },
    'kyubanbomb': {'ja': 'キューバンボム', 'en':  'Suction Bomb', },
    'pointsensor': {'ja': 'ポイントセンサー', 'en':  'Point Sensor', },
    'poison': {'ja': 'ポイズンボール', 'en':  'Disruptor', },
    'quickbomb': {'ja': 'クイックボム', 'en':  'Burst Bomb', },
    'splashbomb': {'ja': 'スプラッシュボム', 'en':  'Splat Bomb', },
    'splashshield': {'ja': 'スプラッシュシールド', 'en':  'Splash Wall', },
    'sprinkler': {'ja': 'スプリンクラー', 'en':  'Sprinkler', },
    'trap': {'ja': 'トラップ', 'en':  'Ink Mine', },
}

deadly_sub_weapons = [
    'chasebomb', 'kyubanbomb', 'quickbomb', 'splashbomb', 'splashshield',
    'sprinkler', 'trap',
]

v1_special_weapons = {
    # v1
    'barrier': {'ja': 'バリア', 'en':  'Bubbler', },
    'bombrush': {'ja': 'ボムラッシュ', 'en':  'Bomb Rush', },
    'daioika': {'ja': 'ダイオウイカ', 'en':  'Kraken', },
    'megaphone': {'ja': 'メガホンレーザー', 'en':  'Killer Wail', },
    'supersensor': {'ja': 'スーパーセンサー', 'en':  'Echolocator', },
    'supershot': {'ja': 'スーパーショット', 'en':  'Inkzooka', },
    'tornado': {'ja': 'トルネード', 'en':  'Inkstrike', },
}

special_weapons = {
    # v2
    'amefurashi': {'ja_JP': 'アメフラシ', 'en': 'Ink Storm', },
    'missiles': {'ja_JP': 'マルチミサイル', 'en': 'Tenta Missiles', },
    'stingray': {'ja_JP': 'ハイパープレッサー', 'en': 'Sting Ray', },
#    'presser': {'ja_JP': 'ハイパープレッサー', 'en': 'Sting Ray', },
    'inkjet': {'ja_JP': 'ジェットパック', 'en': 'Inkjet', },
    'splashdown': {'ja_JP': 'スーパーチャクチ', 'en': 'Splashdown', },
    'chakuchi': {'ja_JP': 'スーパーチャクチ', 'en': 'Splashdown', },
    'armor': {'ja_JP': 'インクアーマー', 'en': 'Ink Armor', },
    'inkstorm': {'ja_JP': 'アメフラシ', 'en': 'Ink Storm', },
    'baller': {'ja_JP': 'イカスフィア', 'en': 'Baller', },
    'blower': {'ja_JP': 'バブルランチャー',  'en': 'Bubble Blower', },
    'booyah': {'ja_JP': 'ナイスダマ', 'en': 'Booyah Bomb', },
    'stamp': {'ja_JP': 'ウルトラハンコ', 'en': 'Ultra Stamp', },
    # 3パターンある
    #'launcher': {'ja': 'スプラッシュボムピッチャー', 'en': 'Bomb Launcher', },
}

deadly_special_weapons = ['daioika', 'megaphone', 'supershot', 'tornado', ]

hurtable_objects = {
    'hoko_shot': {'ja': 'ガチホコショット', 'en': 'Rainmaker Shot', },
    'hoko_barrier': {'ja': 'ガチホコバリア', 'en': 'Rainmaker Shield', },
    'hoko_inksplode': {'ja': 'ガチホコ爆発', 'en': 'Rainmaker Inksplode', },

    'propeller': {'ja': 'プロペラから飛び散ったインク', 'en': 'Ink from a propeller'},
}

hurtable_objects_v2 = {
    'hoko_shot': {'ja': 'ガチホコショット', 'en': 'Rainmaker Shot', },
    'hoko_barrier': {'ja': 'ガチホコバリア', 'en': 'Rainmaker Shield', },
    'hoko_inksplode': {'ja': 'ガチホコ爆発', 'en': 'Rainmaker Inksplode', },

    'splashbomb': {'ja': 'スプラッシュボム', 'en': 'Splat Bomb', },
    'kyubanbomb': {'ja': 'キューバンボム', 'en': 'SuctionBomb', },
    'splashbomb': {'ja': 'スプラッシュボム', 'en': 'Splat Bomb', },
    'robotbomb': {'ja': 'ロボットボム', 'en': 'Autobomb', },

    'amefurashi': {'ja': 'アメフラシ', 'en': 'Ink Storm', },
    'chakuchi': {'ja': 'スーパーチャクチ', 'en': 'Splashdown', },
    'missile': {'ja': 'マルチミサイル', 'en': 'Tenta Missiles', },
    'sprinkler': {'ja': 'スプリンクラー', 'en': 'Splinkler', },
    'sphere': {'ja': 'イカスフィア', 'en': 'Baller', },
    'presser': {'ja': 'ハイパープレッサー', 'en': 'Sting Ray', },
    'jetpack': {'ja': 'ジェットパック', 'en': 'Jetpack' },
    'bubble': {'ja': 'バブルランチャー', 'en': 'Bubble Blower', },
}

additional_cause_of_death_v2 = {
     "amefurashi": {
            "key": "amefurashi",
            "name": {
                "de_DE": "Tintenschauer",
                "en_GB": "Ink Storm",
                "en_US": "Ink Storm",
                "es_ES": "Atormentador",
                "es_MX": "Atormentador",
                "fr_CA": "Pluie d'encre",
                "fr_FR": "Pluie d'encre",
                "it_IT": "Pioggia di colore",
                "ja_JP": "アメフラシ",
                "nl_NL": "Spetterbui",
                "ru_RU": "Туча краски",
                "zh_CN": "墨雨",
                "zh_TW": "墨雨"
            },
        },
        "chakuchi": {
            "key": "chakuchi",
            "name": {
                "de_DE": "Tintenschock",
                "en_GB": "Splashdown",
                "en_US": "Splashdown",
                "es_ES": "Salto explosivo",
                "es_MX": "Clavado",
                "fr_CA": "Choc chromatique",
                "fr_FR": "Choc chromatique",
                "it_IT": "Vernischianto",
                "ja_JP": "スーパーチャクチ",
                "nl_NL": "Superlanding",
                "ru_RU": "Мегаплюх",
                "zh_CN": "砸地",
                "zh_TW": "砸地"
            }
        },
        "missile": {
            "key": "missile",
            "name": {
                "de_DE": "Schwarmraketen",
                "en_GB": "Tenta Missiles",
                "en_US": "Tenta Missiles",
                "es_ES": "Lanzamisiles",
                "es_MX": "Lanzamisiles",
                "fr_CA": "Multi-missile",
                "fr_FR": "Multi-missile",
                "it_IT": "Lanciarazzi",
                "ja_JP": "マルチミサイル",
                "nl_NL": "Spetterraketten",
                "ru_RU": "Каракатница",
                "zh_CN": "跟踪导弹",
                "zh_TW": "跟蹤導彈"
            }
        },
        "nicedama": {
            "key": "nicedama",
            "name": {
                "de_DE": "Booyah Bomb",
                "en_GB": "Booyah Bomb",
                "en_US": "Booyah Bomb",
                "es_ES": "Booyah Bomb",
                "es_MX": "Booyah Bomb",
                "fr_CA": "Booyah Bomb",
                "fr_FR": "Booyah Bomb",
                "it_IT": "Booyah Bomb",
                "ja_JP": "ナイスダマ",
                "nl_NL": "Booyah Bomb",
                "ru_RU": "Booyah Bomb",
                "zh_CN": "好厉害弹",
                "zh_TW": "好厲害彈"
            }
        },
        "sprinkler": {
            "key": "sprinkler",
            "name": {
                "de_DE": "Sprinkler",
                "en_GB": "Sprinkler",
                "en_US": "Sprinkler",
                "es_ES": "Aspersor",
                "es_MX": "Aspersor",
                "fr_CA": "Gicleur",
                "fr_FR": "Fontaine",
                "it_IT": "Spruzzatore",
                "ja_JP": "スプリンクラー",
                "nl_NL": "Inktsprinkler",
                "ru_RU": "Распылятор",
                "zh_CN": "花洒",
                "zh_TW": "花灑"
            }
        },
        "sphere": {
            "key": "sphere",
            "name": {
                "de_DE": "Sepisphäre",
                "en_GB": "Baller",
                "en_US": "Baller",
                "es_ES": "Esfera tintera",
                "es_MX": "Esfera tintera",
                "fr_CA": "Chromo-sphère",
                "fr_FR": "Chromo-sphère",
                "it_IT": "Cromosfera",
                "ja_JP": "イカスフィア",
                "nl_NL": "Barstbubbel",
                "ru_RU": "Шарокат",
                "zh_CN": "仓鼠球",
                "zh_TW": "倉鼠球"
            }
        },
        "sphere_splash": {
            "key": "sphere_splash",
            "name": { # FIXME
                "de_DE": "Sepisphäre",
                "en_GB": "Baller",
                "en_US": "Baller",
                "es_ES": "Esfera tintera",
                "es_MX": "Esfera tintera",
                "fr_CA": "Chromo-sphère",
                "fr_FR": "Chromo-sphère",
                "it_IT": "Cromosfera",
                "ja_JP": "イカスフィアの爆発",
                "nl_NL": "Barstbubbel",
                "ru_RU": "Шарокат",
                "zh_CN": "仓鼠球",
                "zh_TW": "倉鼠球"
            }
        },
        "presser": { # FIXME
            "key": "presser",
            "name": {
                "de_DE": "Hochdruckverunreiniger",
                "en_GB": "Sting Ray",
                "en_US": "Sting Ray",
                "es_ES": "Rayo tintódico",
                "es_MX": "Rayo tintódico",
                "fr_CA": "Pigmalance",
                "fr_FR": "Pigmalance",
                "it_IT": "Baccalaser",
                "ja_JP": "ハイパープレッサー",
                "nl_NL": "Magistraal",
                "ru_RU": "Струятор",
                "zh_CN": "水枪",
                "zh_TW": "水槍"
            }
        },
        "jetpack": {
            "key": "jetpack",
            "name": {
                "de_DE": "Tintendüser",
                "en_GB": "Inkjet",
                "en_US": "Inkjet",
                "es_ES": "Propulsor",
                "es_MX": "Propulsor",
                "fr_CA": "Chromo-jet",
                "fr_FR": "Chromo-jet",
                "it_IT": "Jet splat",
                "ja_JP": "ジェットパック",
                "nl_NL": "Inktjet",
                "ru_RU": "Красколет",
                "zh_CN": "喷墨背包",
                "zh_TW": "噴墨揹包"
            }
        },
        "ultrahanko": {
            "key": "ultrahanko",
            "name": {
                "de_DE": "Ultra-Stempel",
                "en_GB": "Ultra Stamp",
                "en_US": "Ultra Stamp",
                "es_ES": "Ultraselladora",
                "es_MX": "Ultraselladora",
                "fr_CA": "Ultra-tamponneur",
                "fr_FR": "Ultra-tamponneur",
                "it_IT": "Mega timbro",
                "ja_JP": "ウルトラハンコ",
                "nl_NL": "Ultrastempel",
                "ru_RU": "Припечать",
                "zh_CN": "超级邮戳",
                "zh_TW": "超級郵戳"
            }
        },
        "bubble": {
            "key": "bubble",
            "name": {
                "de_DE": "Blubberwerfer",
                "en_GB": "Bubble Blower",
                "en_US": "Bubble Blower",
                "es_ES": "Lanzapompas",
                "es_MX": "Lanzaburbujas",
                "fr_CA": "Lance-bulles",
                "fr_FR": "Lance-bulles",
                "it_IT": "Soffiabolle",
                "ja_JP": "バブルランチャー",
                "nl_NL": "Bellenblazer",
                "ru_RU": "Пузырятор",
                "zh_CN": "泡泡机",
                "zh_TW": "泡泡機"
            }
        },
        "quickbomb": {
            "key": "quickbomb",
            "name": {
                "de_DE": "Insta-Bombe",
                "en_GB": "Burst Bomb",
                "en_US": "Burst Bomb",
                "es_ES": "Bomba rápida",
                "es_MX": "Globo entintado",
                "fr_CA": "Bombe ballon",
                "fr_FR": "Bombe ballon",
                "it_IT": "Granata",
                "ja_JP": "クイックボム",
                "nl_NL": "Ballonbom",
                "ru_RU": "Разрывная бомба",
                "zh_CN": "水球",
                "zh_TW": "水球"
            }
        },
        "splashbomb": {
            "key": "splashbomb",
            "name": {
                "de_DE": "Klecks-Bombe",
                "en_GB": "Splat Bomb",
                "en_US": "Splat Bomb",
                "es_ES": "Bomba básica",
                "es_MX": "Plasbomba",
                "fr_CA": "Bombe splash",
                "fr_FR": "Bombe splash",
                "it_IT": "Bomba splash",
                "ja_JP": "スプラッシュボム",
                "nl_NL": "Klodderbom",
                "ru_RU": "Брызгающая бомба",
                "zh_CN": "三角雷",
                "zh_TW": "三角雷"
            }
        },
        "tansanbomb": {
            "key": "tansanbomb",
            "name": {
                "de_DE": "Sprudel-Bombe",
                "en_GB": "Fizzy Bomb",
                "en_US": "Fizzy Bomb",
                "es_ES": "Bomba carbónica",
                "es_MX": "Bomba carbónica",
                "fr_CA": "Bombe soda",
                "fr_FR": "Bombe soda",
                "it_IT": "Bomba a gassosa",
                "ja_JP": "タンサンボム",
                "nl_NL": "Bomblikje",
                "ru_RU": "Содовая бомба",
                "zh_CN": "碳酸炸弹",
                "zh_TW": "碳酸炸彈"
            }
        },

        "curlingbomb": {
            "key": "curlingbomb",
            "name": {
                "de_DE": "Curling-Bombe",
                "en_GB": "Curling Bomb",
                "en_US": "Curling Bomb",
                "es_ES": "Bomba deslizante",
                "es_MX": "Bomba deslizante",
                "fr_CA": "Bombe curling",
                "fr_FR": "Bombe curling",
                "it_IT": "Bomba curling",
                "ja_JP": "カーリングボム",
                "nl_NL": "Curlingbom",
                "ru_RU": "Керлинг-бомба",
                "zh_CN": "冰壶",
                "zh_TW": "冰壺"
            }
        },
        "kyubanbomb": {
            "key": "kyubanbomb",
            "name": {
                "de_DE": "Haftbombe",
                "en_GB": "Suction Bomb",
                "en_US": "Suction Bomb",
                "es_ES": "Bomba ventosa",
                "es_MX": "Bomba pegajosa",
                "fr_CA": "Bombe gluante",
                "fr_FR": "Bombe gluante",
                "it_IT": "Appiccibomba",
                "ja_JP": "キューバンボム",
                "nl_NL": "Kleefbom",
                "ru_RU": "Бомба на присоске",
                "zh_CN": "粘弹",
                "zh_TW": "粘彈"
            }
        },
        "robotbomb": {
            "key": "robotbomb",
            "name": {
                "de_DE": "Robo-Bombe",
                "en_GB": "Autobomb",
                "en_US": "Autobomb",
                "es_ES": "Robobomba",
                "es_MX": "Robobomba",
                "fr_CA": "Bombe robot",
                "fr_FR": "Bombe robot",
                "it_IT": "Robo-bomba",
                "ja_JP": "ロボットボム",
                "nl_NL": "Robobom",
                "ru_RU": "Робобомба",
                "zh_CN": "小鸡炸弹",
                "zh_TW": "小雞炸彈"
            }
        },

        "splashshield": {
            "name": {
                "de_DE": "Tintenwall",
                "en_GB": "Splash Wall",
                "en_US": "Splash Wall",
                "es_ES": "Telón de tinta",
                "es_MX": "Barricada",
                "fr_CA": "Mur d'encre",
                "fr_FR": "Mur d'encre",
                "it_IT": "Muro di colore",
                "ja_JP": "スプラッシュシールド",
                "nl_NL": "Inktgordijn",
                "ru_RU": "Чернильный занавес",
                "zh_CN": "雨帘",
                "zh_TW": "雨簾"
            }
        },
        "torpedo": {
            "key": "torpedo",
            "name": {
                "de_DE": "Torpedo",
                "en_GB": "Torpedo",
                "en_US": "Torpedo",
                "es_ES": "Torpedo",
                "es_MX": "Torpedo",
                "fr_CA": "Torpedo",
                "fr_FR": "Torpedo",
                "it_IT": "Torpedo",
                "ja_JP": "トーピード",
                "nl_NL": "Torpedo",
                "ru_RU": "Torpedo",
                "zh_CN": "鱼雷",
                "zh_TW": "魚雷"
            }
        },
        "trap": {
            "key": "trap",
            "name": {
                "de_DE": "Tintenmine",
                "en_GB": "Ink Mine",
                "en_US": "Ink Mine",
                "es_ES": "Bomba trampa",
                "es_MX": "Mina de tinta",
                "fr_CA": "Mine d'encre",
                "fr_FR": "Mine",
                "it_IT": "Mina",
                "ja_JP": "トラップ",
                "nl_NL": "Inktmijn",
                "ru_RU": "Мина",
                "zh_CN": "地雷",
                "zh_TW": "地雷"
            }
        },

        "hoko_shot": {
            "key": "hoko_shot",
            "name": {
                "de_DE": "Rainmaker Shot",
                "en_GB": "Rainmaker Shot",
                "en_US": "Rainmaker Shot",
                "es_ES": "Rainmaker Shot",
                "es_MX": "Rainmaker Shot",
                "fr_CA": "Rainmaker Shot",
                "fr_FR": "Rainmaker Shot",
                "it_IT": "Rainmaker Shot",
                "ja_JP": "ホコショット",
                "nl_NL": "Rainmaker Shot",
                "ru_RU": "Rainmaker Shot",
                "zh_CN": "Rainmaker Shot",
                "zh_TW": "Rainmaker Shot"
            }
        },
        "hoko_barrier": {
            "key": "hoko_barrier",
            "name": {
                "de_DE": "Rainmaker Barrier",
                "en_GB": "Rainmaker Barrier",
                "en_US": "Rainmaker Barrier",
                "es_ES": "Rainmaker Barrier",
                "es_MX": "Rainmaker Barrier",
                "fr_CA": "Rainmaker Barrier",
                "fr_FR": "Rainmaker Barrier",
                "it_IT": "Rainmaker Barrier",
                "ja_JP": "ガチホコのバリア",
                "nl_NL": "Rainmaker Barrier",
                "ru_RU": "Rainmaker Barrier",
                "zh_CN": "Rainmaker Barrier",
                "zh_TW": "Rainmaker Barrier"
            }
        },
    }
oob_reasons = {
    'oob': {'ja': '場外', 'en': 'Out of Bounds', },
    'fall': {'ja': '転落', 'en': 'Fall', },
    'drown': {'ja': '水死', 'en': 'Drowning', },
}

udemae_strings = [
    's+', 's', 'a+', 'a', 'a-', 'b+', 'b', 'b-', 'c+', 'c', 'c-'
]

fes_rank_titles = [
    'fanboy', 'fiend', 'defender', 'champion', 'king'
]


gear_abilities = {
    'bomb_range_up': {'ja': 'ボム飛距離アップ', 'en': 'Bomb Range Up'},
    'bomb_sniffer': {'ja': 'ボムサーチ', 'en': 'Bomb Sniffer'},
    'cold_blooded': {'ja': 'マーキングガード', 'en': 'Cold Blooded'},
    'comeback': {'ja': 'カムバック', 'en': 'Comeback'},
    'damage_up': {'ja': '攻撃力アップ', 'en': 'Damage Up'},
    'defense_up': {'ja': '防御力アップ', 'en': 'Defense Up'},
    'empty': {'ja': '空', 'en': 'Empty'},
    'haunt': {'ja': 'うらみ', 'en': 'Haunt'},
    'ink_recovery_up': {'ja': 'インク回復力アップ', 'en': 'Ink Recovery Up'},
    'ink_resistance_up': {'ja': '安全シューズ', 'en': 'Ink Resistance'},
    'ink_saver_main': {'ja': 'インク効率アップ（メイン）', 'en': 'Ink Saver (Main)'},
    'ink_saver_sub': {'ja': 'インク効率アップ（サブ）', 'en': 'Ink Saver (Sub)'},
    'last_ditch_effort': {'ja': 'ラストスパート', 'en': 'Last-Ditch Effort'},
    'locked': {'ja': '未開放', 'en': 'Locked'},
    'ninja_squid': {'ja': 'イカニンジャ', 'en': 'Ninja Squid'},
    'opening_gambit': {'ja': 'スタートダッシュ', 'en': 'Opening Gambit'},
    'quick_respawn': {'ja': '復活時間短縮', 'en': 'Quick Respawn'},
    'quick_super_jump': {'ja': 'スーパージャンプ時間短縮', 'en': 'Quick Super Jump'},
    'recon': {'ja': 'スタートレーダー', 'en': 'Recon'},
    'run_speed_up': {'ja': 'ヒト移動速度アップ', 'en': 'Run Speed Up'},
    'special_charge_up': {'ja':  'スペシャル増加量アップ', 'en': 'Special Charge Up'},
    'special_duration_up': {'ja':  'スペシャル時間延長', 'en': 'Special Duration Up'},
    'special_saver': {'ja':  'スペシャル減少量ダウン', 'en': 'Special Saver'},
    'stealth_jump': {'ja':  'ステルスジャンプ', 'en': 'Stealth Jump'},
    'swim_speed_up': {'ja':  'イカダッシュ速度アップ', 'en': 'Swim Speed Up'},
    'tenacity': {'ja':  '逆境', 'en': 'Tenacity'}
}

gear_brands = {
    'amiibo':     {'ja': 'amiibo', 'en': 'amiibo', },
    'cuttlegear': {'ja': 'アタリメイド', 'en': 'Cuttlegear', },
    'famitsu':    {'ja': 'ファミ通', 'en': 'Famitsu', },
    'firefin':    {'ja': 'ホッコリー', 'en': 'Firefin', },
    'forge':      {'ja': 'Forge', 'en': 'Forge', },
    'inkline':    {'ja': 'Inkline', 'en': 'Inkline', },
    'kog':        {'ja': 'KOG', 'en': 'KOG', },
    'krakon':     {'ja': 'クラーゲス', 'en': 'Krak-On', },
    'rockenberg': {'ja': 'ロッケンベルグ', 'en': 'Rockenberg', },
    'skalop':     {'ja': 'ホタックス', 'en': 'Skalop', },
    'splashmob':  {'ja': 'ジモン', 'en': 'Splash Mob', },
    'squidforce': {'ja': 'バトロイカ', 'en': 'Squidforce', },
    'squidgirl':  {'ja': '侵略！イカ娘', 'en': 'SQUID GIRL', },
    'takoroka':   {'ja': 'ヤコ', 'en': 'Takoroka', },
    'tentatek':   {'ja': 'アロメ', 'en': 'Tentatek', },
    'zekko':      {'ja': 'エゾッコ', 'en': 'Zekko', },
    'zink':       {'ja': 'アイロニック', 'en': 'Zink', },
}

lobby_types = {
    'festa':    {'ja': 'フェス', 'en': 'Splatfest'},
    'private':  {'ja': 'プライベートマッチ', 'en': 'Private Battle'},
    'public':   {'ja': '通常マッチ', 'en': 'Standard Battle'},
    'tag':      {'ja': 'タッグマッチ', 'en': 'Squad Battle'},
}

#

upcoming_weapons = [
]

#

for ability in gear_abilities.keys():
    gear_abilities[ability]['id'] = ability

for brand in gear_brands.keys():
    gear_brands[brand]['id'] = brand

#

stages_v1 = statink_json.import_stages('data/spl1/stages.json')
weapons_v1 = statink_json.import_weapons('data/spl1/weapons.json')
stages_v2 = statink_json.import_stages('data/spl2/stages.json')
weapons_v2 = statink_json.import_weapons('data/spl2/weapons.json')

cause_of_death_v2 = weapons_v2.copy()
cause_of_death_v2.update(additional_cause_of_death_v2)
