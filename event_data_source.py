# ==========================================
# イベントデータ定義
# ==========================================
# 形式: "イベントID": [ イベント1, イベント2, ... ]
#
#   {"type": "text", "content": ["ページ1", "ページ2"]}  -> テキスト表示
#   {"type": "pattern", "content": ["単語"]}            -> パターン再生
# ==========================================

event_data = {
    "TRAIN_INTRO": [
        {
            "type": "text", 
            "content": [
                "…意識が浮上する。魂が抜け落ちた器のように、私は電車の長椅子に横たわっていた。",
                "視界に入った食堂の椅子に座り直し、沸騰した思考を冷まそうとするが、頭は鉛のように重い。",
            ]
        },
        {
            "type": "pattern", 
            "content": ["近づける"]
        },
        {
            "type": "text", 
            "content": [
                "この音は、私を呼ぶ声だ。向こうの教室から聴こえてくる。",
                "言葉としては認識できない。その欠落ゆえに、施設に隔離されている。",
                "今日のリハビリに戻ろう。"
            ]
        }
    ],
    "DAY_BED_INTRO_2": [
        {
            "type": "text", 
            "content": [
                "…また朝が来たようだ。ここに来てから、朝の訪れるタイミングは掴めないままだ。",
                "昨夜、あるいはそう思われる時間も、暗闇は音もなく、スイッチが切られるように突然だった。"
            ]
        },
        {
            "type": "pattern", 
            "content": ["何", "距離"]
        },
        {
            "type": "text", 
            "content": [
                "頭上からは、昨日に増して甲高い声の連呼が響き始めている。"
            ]
        },
    ],
    "DAY_BED_INTRO_3": [
        {
            "type": "text", 
            "content": [
                "昨日と今日の違いを探して、すぐにやめた。",
                "…いつかこの白濁した環境を脱する時が来たとして、果たしてそれは幸せだろうか。"
            ]
        },
        {
            "type": "pattern", 
            "content": ["生", "終", "←", "死", "始"]
        },
        {
            "type": "text", 
            "content": [
                "…あるいは、ここに同じ年齢ほどの異性がもう一人放り込まれたとして、私は望まれた行動をとるだろうか。",
                "子どもも、そのまた子どもだって、運命は決まっているのに。"
            ]
        },
    ],
    "DAY_BED_INTRO_4": [
        {
            "type": "text", 
            "content": [
                "何かを変えるには、何かが変わらなければならない。",
                "それも完成間近だ。膝にこびりついた白い石膏の粉を、静かに払い落とす。"
            ]
        },
        {
            "type": "pattern", 
            "content": ["何", "善悪", "⇔", "神為", "時", "+", "壊す"]
        },
    ],
    "DAY_BED_INTRO_5": [
        {
            "type": "pattern", 
            "content": ["神為", "距離", "+", "得る", "→", "善悪", "-", "&", "失う", "→", "善悪", "+"]
        },
    ],
    "DAY_BED_INTRO_6": [
        {
            "type": "text", 
            "content": [
                "看護師は来ない。医師も来ない。",
                "今日のリハビリは始まっている。"
            ]
        },
    ],
    "DAY_BED_INTRO_14": [
        {
            "type": "text", 
            "content": [
                "",
                "",
                ""
            ]
        },
    ],
    "DAY_CLASSROOM_TO_ROOM_1": [
        {
            "type": "text",
            "content": [
                "脈絡なく、目的もなく、ただ既製の風景が連続して存在する。",
                "不自然な箱舟のような空間に閉じ込められている。"
            ]
        },
        {
            "type": "pattern", 
            "content": ["時", "+"]
        },
        {
            "type": "text", 
            "content": [
                "教室に入ると、黒板の向こうから聴こえていたその声はやむ。",
                "教卓の上には、オセロ盤のようなものが置かれている。"]
        }
    ],
    "DAY_CLASSROOM_TO_ROOM_2": [
        {
            "type": "text",
            "content": [
                "床には靴の跡ひとつなく、壁の隅にも埃は溜まっていない。生活の痕跡を消し去った無菌のゆりかごだ。",
                "黒板にはチョークの粉さえ残っていない。じっと見つめていると、壁の向こう側にある空間まで見通せるのではないかと錯覚するほどだった。"
            ]
        }
    ],
    "DAY_TRAIN_TO_ROOM_1": [
        {
            "type": "text",
            "content": [
                "それぞれの区画はドアで区切られることがない。それでも、毎日繰り返す往復運動の中では、この電車内を横切る必要がある。",
                "動き出すことのない電車は、まるで廊下のように振る舞っている。",
            ]
        }
    ],
    "DAY_TRAIN_TO_ROOM_3": [
        {
            "type": "text",
            "content": [
                "座席に腰掛けると、どこかへ運ばれている錯覚に陥る。だが、そこにはかつて誰かが座ったへこみも、使い古された柔らかさもない。",
                "吊り革は揺れている。我々を乗せて。",
            ]
        }
    ],
    "DAY_TRAIN_TO_ROOM_6": [
        {
            "type": "text",
            "content": [
                "",
                "吊り革は揺れ続けている。身長も、体重も、誤差に過ぎない。",
            ]
        }
    ],
    "DAY_ATELIER_TO_TRAIN_1": [
        {
            "type": "text",
            "content": [
                "大きなキャンバスがある。絵の具や筆があれば思考を整理できるだろう。",
                "もっとも、期待された使い方とは違うようだが。",
            ]
        }
    ],
    "DAY_ATELIER_TO_TRAIN_5": [
        {
            "type": "text",
            "content": [
                "ここだけだ。乱雑さを残しているのは。私はそれに気づき、忘れかけていた苛立ちを覚えた。",
            ]
        }
    ],
    "POND_TO_ATELIER": [
        {
            "type": "text",
            "content": [
                "大きな釣り堀か、プールか。はたまたただの貯水池かもしれない。",
                "水は澄んでいるものの、安全な液体である保証はどこにもない。",
            ]
        }
    ],
    "DAY_HOSPICE_TO_ATELIER_1": [
        {
            "type": "text",
            "content": [
                "眠る場所は、病室の一画が充てられている。",
                "退院を目指すには、毎日多大な労力を消耗する。一日を終える前には、そこらにあるシーツで体を拭いたいものだ。",
            ]
        }
    ],
    "DAY_HOSPICE_TO_ATELIER_2": [
        {
            "type": "text",
            "content": [
                "もとの生活を出来る限り取り戻すための生活。退院できても、以前より不自由さが残ることこそあれ、ましになることはない。",
                "そのために今、何を優先すべきか。答えは見つからない。",
            ]
        }
    ],
    "DAY_HOSPICE_TO_ATELIER_4": [
        {
            "type": "text",
            "content": [
                "もし私が今日死んだとしたら、次の患者を診るためにここをもう一度使うのだろうか。",
                "その患者は何番目で、私は何番目だったのだろうか。",
            ]
        }
    ],
    "BOARD_INTRO": [
        {
            "type": "text",
            "content": ["…軽く息を吐いてから、勉強机の上に座った。"]
        }
    ],
    "BOARD_PASSED": [
        {
            "type": "text",
            "content": [
                "…声がやんだ。成績はどうだったのだろうか。",
                "食事が提供された。座って食べよう。",
            ]
        }
    ],
    "BOARD_ALREADY_USED": [
        {
            "type": "text",
            "content": ["もう声は聴こえてこない。"]
        }
    ],
    "EAT_CHOICE": [
        {
            "type": "text",
            "content": ["ここで食べようか。"]
        }
    ],
    "EAT_ACTION": [
        {
            "type": "text",
            "content": ["…ごちそうさまです。"]
        }
    ],
    "EAT_CANCEL": [
        {
            "type": "text",
            "content": ["いや、他の場所がいい。"]
        }
    ],
    "GOOD_MEAL": [
        {
            "type": "text",
            "content": [
                "見た目こそ嫌悪感を誘うが、味は美味い。",
                "食べ物を口に運ぶ手は止まらず、一気に平らげてしまった。"
            ]
        }
    ],
    "BAD_MEAL": [
        {
            "type": "text",
            "content": [
                "質素な病院食だ。リハビリ中だから我慢しなければ。",
                "一口ずつ、噛みしめるようにゆっくりと味わった。"
            ]
        }
    ],
    "FOOD": [
        {
            "type": "text",
            "content": ["コンビニ弁当。病院食よりはいくらか気の紛れる味わいだ。"]
        }
    ],
    "NO_MEAL": [
        {
            "type": "text",
            "content": [
                "座ってみる。",
                "…誰かに見られている感覚に陥る。"
            ]
        }
    ],
    "BATH_CHOICE": [
        {
            "type": "text",
            "content": ["施設の中で唯一の水場だ。これが水と呼べるものならば。"]
        }
    ],
    "BATH_ACTION": [
        {
            "type": "text",
            "content": ["…肌が一層ねばつくようになった気もする。"]
        }
    ],
    "TOILET_CHOICE": [
        {
            "type": "text",
            "content": ["トイレの形をしているが、水は通っていない。"]
        }
    ],
    "TOILET_RECHOICE": [
        {
            "type": "text",
            "content": ["くぼんだ石が異臭を放っている。"]
        }
    ],
    "TOILET_REFRESH": [
        {
            "type": "text",
            "content": ["これがしたかった。"]
        }
    ],
    "TOILET_RECHOICE_REFRESH": [
        {
            "type": "text",
            "content": ["…これで多少は臭わなくなった。"]
        }
    ],
    "TOILET_ACTION": [
        {
            "type": "text",
            "content": ["…不思議と安心感がある。"]
        }
    ],
    "TOILET_BADACTION": [
        {
            "type": "text",
            "content": ["…良い心地はしない。"]
        }
    ],
    "TOILET_CANCEL": [
        {
            "type": "text",
            "content": ["そうだ。尊厳を保たないといけない。そこに理由などないとしても。"]
        }
    ],
    "SHOP_CHOICE": [
        {
            "type": "text",
            "content": ["食べ物はここにいくらでもある。"]
        }
    ],
    "SHOP_ACTION": [
        {
            "type": "text",
            "content": ["快適な生活が先決だ。"]
        }
    ],
    "SHOP_CANCEL": [
        {
            "type": "text",
            "content": ["しかし、対価なしに持っていくわけにはいかない。"]
        }
    ],
    "NONAVAILABLE": [
        {
            "type": "text",
            "content": ["手が空いているときにまた見に来よう。"]
        }
    ],
    "CHARCOAL_CHOICE": [
        {
            "type": "text",
            "content": ["チャコールスティックだ。"]
        }
    ],
    "CHARCOAL_ACTION": [
        {
            "type": "text",
            "content": ["これは役に立つぞ。"]
        }
    ],
    "CHARCOAL_CANCEL": [
        {
            "type": "text",
            "content": ["欲してはいないが。"]
        }
    ],
    "SHEETS_CHOICE": [
        {
            "type": "text",
            "content": ["体のべたつきが気になる。"]
        }
    ],
    "SHEETS_ACTION": [
        {
            "type": "text",
            "content": ["気持ちがいい。"]
        }
    ],
    "SHEETS_CANCEL": [
        {
            "type": "text",
            "content": ["…そうでもないか。"]
        }
    ],
    "REST": [
        {
            "type": "text",
            "content": ["まだ眠気は受け取っていない。"]
        }
    ],
    "TOILET": [
        {
            "type": "text",
            "content": ["その前にどうしても用を足す必要がある。"]
        }
    ],
    "HUNGER": [
        {
            "type": "text",
            "content": ["空腹が睡眠を妨げている。"]
        }
    ],
    "QUESTION_SKIP_PENALTY": [
        {
            "type": "text",
            "content": ["分からない。これは黙秘しよう。"]
        }
    ],
    "draw": [
        {
            "type": "text",
            "content": ["何か描く物はないだろうか。クレヨンや鉛筆でもいい。"]
        }
    ],
    "finish": [
        {
            "type": "text",
            "content": ["…よし、覚えた。これでいつでも思い出せる。チャコールは戻しておこう。"]
        }
    ],
    "GAME_OVER_1": [
        {
            "type": "text",
            "content": [
                "目を覚ますと、私はまた、あの冷たく無機質な独房にいた。どうやら、リハビリは打ち切りとなったようだ。",
                "背後には、彼らがいる。",
            ]
        },
        {
            "type": "pattern", 
            "content": ["終"]
        },
            {
                "type": "text",
                "content": [
                    "始まりの時と同じように、私は自分の手で、退院の同意を強要された。",
                    "役割を終えた実験動物の行く末を、私は嫌というほど知っている。",
                ]
            },
    ],
    "GAME_OVER_2": [
        {
            "type": "text",
            "content": [
                "…目を覚ますと、私は見知らぬ施設にいた。軽く見回ってみると、脈絡なく、目的もなく、ただ既製の風景が連続して存在する。",
                "キャンバスには、前人たちの歴史が刻まれている。誰かの体温が残っているような気がした。",
                "エンディング3 LR7: 人員の死",
            ]
        }
    ],
    "GAME_CLEAR": [
        {
            "type": "text",
            "content": [
                "目を覚ますと、場違いなほどに小綺麗な食卓だった。",
                "異なるのは、首の周りに重厚で、温かな感触があることだった。ノイズだった声の意味が、脳へ直接流れ込んでくる。",
                "言葉というよりも、ずっと純粋で、暴力的な理解だ。",
            ]
        },
        {
            "type": "pattern", 
            "content": ["得る"]
        },
        {
            "type": "text",
            "content": [
                "＜良くやった。おめでとう。＞",
                "＜君は晴れて、我々の、従順で賢く、可愛らしい愛玩動物と認められた。＞",
            ]
        },
        {
            "type": "pattern", 
            "content": ["得る", "得る", "得る", "得る", "得る", "得る", "得る"]
        },
        {
            "type": "text",
            "content": [
                "＜良くやった！良くやった！良くやった！良くやった！良くやった！良くやった！良くやった！＞",
                "視界が祝福の文字で埋め尽くされる。一文字刻まれるごとに人間としての尊厳は摩耗し、報酬への渇望が全身を上書きしていく。",
                "＜そうだ。君には伴侶も用意しているよ。＞",
                "そう言って見せられたのは、人間と呼ぶには原型を留めていない何かだった。",
                "かつての同胞の面影を残しながらも、彼らにとって都合の良い機能だけを備えた異形へと変貌している。",
                "＜次の実験に進もう。さぁ、より優れたペットを共に創っていこうじゃないか。＞",
                "自然と笑みがこぼれる。私は、これ以上ないほど幸福だった。管理される喜びこそ、私が求めていた未来だったのだから。",
            ]
        },
        {
            "type": "pattern", 
            "content": ["生", "終", "←", "死", "始"]
        },
        {
            "type": "text",
            "content": [
                "エンディング2 LR7: 人格の死"
            ]
        },
        
    ],
    "GAME_CLEAR_TRUE": [
        {
            "type": "text",
            "content": [
                "目を覚ますと、私は他の被収容者たちと共に、処置を待つための広い部屋へ移送されていた。",
                "私は彼らの目的を理解した。だが、彼らは私の沈黙と意思を理解することはなかった。",
                "彼らが与えようとしたのは家畜としての安寧であり、私が守り抜いたのは人間としての呪いだった。",
                "私は彼らの傲慢さを知った上で、聴くことを諦めなかった。だが、彼らは診ることを諦めた。",
            ]
        }
    ],
    "TRUE_ACTION": [
        {
            "type": "text",
            "content": [
                "＜制御不能であり、加害性を残す野生生物は、即刻駆除すべきである。＞",
                "我々は文明という名のコンクリートの箱から解き放たれた。"
                "放たれた閃光は、予想よりも静かだった。言葉は、予想よりも早く意味を失った。",
                "エンディング1 LR7: 人類の死"
            ]
        }
    ],
    "TITLE": [
        {
            "type": "text",
            "content": ["言語療法室 LR7"]
        }
    ],
    "RELEASE_MASTER": [
        {
            "type": "text",
            "content": ["次の被験者として、音から文字への自動変換が可能な【Master】がやってきた。"]
        }
    ],
    "RELEASE_DOCTOR": [
        {
            "type": "text",
            "content": ["度重なる品種改良により、音から文字、そして語彙への自動変換が可能な【Doctor】が産まれた。"]
        }
    ],
    "GAME_END": [
        {
            "type": "text",
            "content": [
                 "コンクリートが瓦解し、収容所が崩壊してからどれほど経っただろうか。",
                 "ひしゃげたトタンの影に身を寄せ、無造作に投げ出された小包の中から未開封のペットボトルを引きずり出した。",
                 "小包の残りは、2ダースと4本だった。",
                 "背後で砂を蹴る音がする。振り返ると、柔らかな毛皮をまとった小動物が必死に穴を掘っていた。",
                 "「…お前も、独りか。」\n声が、ひび割れた唇からこぼれる。",
                 "生き残ったことが幸運なのか、罰なのか、判断はつかない。ただ、我々は奇妙な同胞だった。",
                 "小動物が顔を上げ、じっと私を射抜く。激しく浅い呼吸が、焦げ付いた空気を懸命に吸い込んでいた。",
                 "「喉、乾いているのか？」\nプラスチックの封を切る音が荒野に響く。",
                 "小動物の目線の高さまでそれを下ろし、脅かさないよう指先で滑らせた。",
                 "しばらくの間を置いて、小動物は距離を詰める。水を舐める音が、かすかに聞こえ始めた。",
                 "「美味いだろ。」\nふいに、音が止まる。",
                 "水滴を滴らせた口元、その瞳がまっすぐに私を捉えていた。突如、それはひと吠えすると、ガレキの隙間へと姿を消した。",
                 "刹那、先ほどよりも大きな遠吠えが響く。愚かにも私は、ここでようやく彼らとの同一性に気づいたのだ。",
                 "2ダースと4本。1日1本換算で、ちょうど4週間分だった。"
            ]
        }
    ],
}

event_en_data = {
    "TRAIN_INTRO": [
        {
            "type": "text", 
            "content": [
                "...My consciousness surfaces. I was lying on the long bench of a train, like a vessel whose soul had fallen out.",
                "I sit back in the dining chair that came into view, trying to cool my boiling thoughts, but my head feels heavy as lead.",
            ]
        },
        {
            "type": "pattern", 
            "content": ["近づける"]
        },
        {
            "type": "text", 
            "content": [
                "This sound is a voice calling me. It's coming from the classroom over there.",
                "I cannot recognize it as language. Because of that deficiency, I am isolated in this facility.",
                "Time to return to today's rehabilitation."
            ]
        }
    ],
    "DAY_BED_INTRO_2": [
        {
            "type": "text", 
            "content": [
                "...It seems morning has come again. Since arriving here, I still haven't grasped the timing of the morning's arrival.",
                "Last night-or what seemed like it-the darkness was silent, sudden as if a switch had been flipped."
            ]
        },
        {
            "type": "pattern", 
            "content": ["何", "距離"]
        },
        {
            "type": "text", 
            "content": [
                "From above, a chorus of high-pitched voices has begun to echo, even more so than yesterday."
            ]
        },
    ],
    "DAY_BED_INTRO_3": [
        {
            "type": "text", 
            "content": [
                "I looked for the difference between yesterday and today, then stopped immediately.",
                "...If the time ever comes to escape this opaque environment, would that actually be happiness?"
            ]
        },
        {
            "type": "pattern", 
            "content": ["生", "終", "←", "死", "始"]
        },
        {
            "type": "text", 
            "content": [
                "...Or, if another person of about the same age and opposite sex were thrown in here, would I take the desired actions?",
                "Children, and even their children-their fates are already decided."
            ]
        },
    ],
    "DAY_BED_INTRO_4": [
        {
            "type": "text", 
            "content": [
                "For something to change, something must change.",
                "It is nearly complete. I quietly brush the white plaster dust off my knees."
            ]
        },
        {
            "type": "pattern", 
            "content": ["何", "善悪", "⇔", "神為", "時", "+", "壊す"]
        },
    ],
    "DAY_BED_INTRO_5": [
        {
            "type": "pattern", 
            "content": ["神為", "距離", "+", "得る", "→", "善悪", "-", "&", "失う", "→", "善悪", "+"]
        },
    ],
    "DAY_BED_INTRO_6": [
        {
            "type": "text", 
            "content": [
                "No nurses come. No doctors come.",
                "Today's rehabilitation has begun."
            ]
        },
    ],
    "DAY_BED_INTRO_14": [
        {
            "type": "text", 
            "content": [
                "",
                "",
                ""
            ]
        },
    ],
    "DAY_CLASSROOM_TO_ROOM_1": [
        {
            "type": "text",
            "content": [
                "Without context or purpose, ready-made landscapes simply exist in sequence.",
                "I am trapped in a space like an unnatural ark."
            ]
        },
        {
            "type": "pattern", 
            "content": ["時", "+"]
        },
        {
            "type": "text", 
            "content": [
                "As I enter the classroom, the voice that was hearing from beyond the blackboard ceases.",
                "Something like an Othello board is placed on the teacher's desk."]
        }
    ],
    "DAY_CLASSROOM_TO_ROOM_2": [
        {
            "type": "text",
            "content": [
                "There isn't a single footprint on the floor, and no dust has gathered in the corners of the walls.",
                "It is a sterile cradle that has erased all traces of life.",
                "Not even chalk dust remains on the blackboard.", 
                "Staring at it, I had the illusion that I could see right through to the space on the other side of the wall."
            ]
        }
    ],
    "DAY_TRAIN_TO_ROOM_1": [
        {
            "type": "text",
            "content": [
                "Each section is not divided by doors.",
                "Still, in the daily cycle of back-and-forth movement, it is necessary to cross through this train car.",
                "The train, which never moves, behaves just like a hallway.",
            ]
        }
    ],
    "DAY_TRAIN_TO_ROOM_3": [
        {
            "type": "text",
            "content": [
                "Sitting in the seat gives the illusion of being carried somewhere.",
                "However, there is no dent where someone once sat, nor any worn-out softness.",
                "The hand straps are swinging. Carrying us.",
            ]
        }
    ],
    "DAY_TRAIN_TO_ROOM_6": [
        {
            "type": "text",
            "content": [
                "",
                "The hand straps continue to swing. Height and weight are nothing more than margins of error.",
            ]
        }
    ],
    "DAY_ATELIER_TO_TRAIN_1": [
        {
            "type": "text",
            "content": [
                "There is a large canvas. If I had paints and brushes, I could organize my thoughts.",
                "Though, it seems they expect it to be used differently.",
            ]
        }
    ],
    "DAY_ATELIER_TO_TRAIN_5": [
        {
            "type": "text",
            "content": [
                "This is the only place. The only one that remains cluttered.",
                "Noticing this, I felt a long-forgotten irritation.",
            ]
        }
    ],
    "POND_TO_ATELIER": [
        {
            "type": "text",
            "content": [
                "A large fishing pond, or a pool. Or perhaps just a reservoir.",
                "The water is clear, but there's no guarantee it's a safe liquid.",
            ]
        }
    ],
    "DAY_HOSPICE_TO_ATELIER_1": [
        {
            "type": "text",
            "content": [
                "A section of a hospital room is assigned as the sleeping area.",
                "Aiming for discharge consumes a vast amount of effort every day.",
                "Before ending the day, I'd like to wipe my body with any available sheets.",
            ]
        }
    ],
    "DAY_HOSPICE_TO_ATELIER_2": [
        {
            "type": "text",
            "content": [
                "A life lived to regain former life as much as possible.",
                "Even if discharged, things won't get better; there will only be more lingering restrictions than before.",
                "What should be prioritized now for that purpose? I can't find the answer.",
            ]
        }
    ],
    "DAY_HOSPICE_TO_ATELIER_4": [
        {
            "type": "text",
            "content": [
                "If I were to die today, would they use this place again for the next patient?",
                "What number would that patient be, and what number was I?",
            ]
        }
    ],
    "BOARD_INTRO": [
        {
            "type": "text",
            "content": ["...Letting out a soft breath, I sat at the study desk."]
        }
    ],
    "BOARD_PASSED": [
        {
            "type": "text",
            "content": [
                "...The voice stopped. I wonder how my grades were.",
                "A meal has been provided. Let's sit and eat.",
            ]
        }
    ],
    "BOARD_ALREADY_USED": [
        {
            "type": "text",
            "content": ["The voice can no longer be heard."]
        }
    ],
    "EAT_CHOICE": [
        {
            "type": "text",
            "content": ["Shall I eat here?"]
        }
    ],
    "EAT_ACTION": [
        {
            "type": "text",
            "content": ["...Thank you for the meal."]
        }
    ],
    "EAT_CANCEL": [
        {
            "type": "text",
            "content": ["No, somewhere else is better."]
        }
    ],
    "GOOD_MEAL": [
        {
            "type": "text",
            "content": [
                "The appearance invites disgust, but the taste is delicious.",
                "My hand didn't stop moving food to my mouth, and I finished it all at once."
            ]
        }
    ],
    "BAD_MEAL": [
        {
            "type": "text",
            "content": [
                "Simple hospital food. I have to endure it since I'm in rehabilitation.",
                "I savored it slowly, one bite at a time."
            ]
        }
    ],
    "FOOD": [
        {
            "type": "text",
            "content": ["A convenience store bento. It's a taste that's somewhat more distracting than hospital food."]
        }
    ],
    "NO_MEAL": [
        {
            "type": "text",
            "content": [
                "I try sitting down.",
                "...I fall into the sensation of being watched by someone."
            ]
        }
    ],
    "BATH_CHOICE": [
        {
            "type": "text",
            "content": ["The only watering hole in the facility. If this can be called water."]
        }
    ],
    "BATH_ACTION": [
        {
            "type": "text",
            "content": ["...I feel like my skin has become even more sticky."]
        }
    ],
    "TOILET_CHOICE": [
        {
            "type": "text",
            "content": ["It has the shape of a toilet, but no water runs through it."]
        }
    ],
    "TOILET_RECHOICE": [
        {
            "type": "text",
            "content": ["The hollowed-out stone is emitting a foul odor."]
        }
    ],
    "TOILET_REFRESH": [
        {
            "type": "text",
            "content": ["This is what I wanted to do."]
        }
    ],
    "TOILET_RECHOICE_REFRESH": [
        {
            "type": "text",
            "content": ["...Now it smells a bit less."]
        }
    ],
    "TOILET_ACTION": [
        {
            "type": "text",
            "content": ["...Strangely, there is a sense of security."]
        }
    ],
    "TOILET_BADACTION": [
        {
            "type": "text",
            "content": ["...It doesn't feel good."]
        }
    ],
    "TOILET_CANCEL": [
        {
            "type": "text",
            "content": ["That's right. I must maintain my dignity. Even if there's no reason for it."]
        }
    ],
    "SHOP_CHOICE": [
        {
            "type": "text",
            "content": ["There is plenty of food here."]
        }
    ],
    "SHOP_ACTION": [
        {
            "type": "text",
            "content": ["A comfortable life is the first priority."]
        }
    ],
    "SHOP_CANCEL": [
        {
            "type": "text",
            "content": ["However, I cannot take them without providing something in return."]
        }
    ],
    "NONAVAILABLE": [
        {
            "type": "text",
            "content": ["I'll come back to check when I have some free time."]
        }
    ],
    "CHARCOAL_CHOICE": [
        {
            "type": "text",
            "content": ["It's a charcoal stick."]
        }
    ],
    "CHARCOAL_ACTION": [
        {
            "type": "text",
            "content": ["This will be useful."]
        }
    ],
    "CHARCOAL_CANCEL": [
        {
            "type": "text",
            "content": ["Not that I desire it, though."]
        }
    ],
    "SHEETS_CHOICE": [
        {
            "type": "text",
            "content": ["The stickiness of my body is bothersome."]
        }
    ],
    "SHEETS_ACTION": [
        {
            "type": "text",
            "content": ["This feels good."]
        }
    ],
    "SHEETS_CANCEL": [
        {
            "type": "text",
            "content": ["...Maybe not."]
        }
    ],
    "REST": [
        {
            "type": "text",
            "content": ["I haven't received sleepiness yet."]
        }
    ],
    "TOILET": [
        {
            "type": "text",
            "content": ["Before that, I absolutely need to relieve myself."]
        }
    ],
    "HUNGER": [
        {
            "type": "text",
            "content": ["Hunger is preventing sleep."]
        }
    ],
    "QUESTION_SKIP_PENALTY": [
        {
            "type": "text",
            "content": ["I don't know. I'll remain silent."]
        }
    ],
    "draw": [
        {
            "type": "text",
            "content": ["Isn't there anything to draw with? Crayons or pencils would do."]
        }
    ],
    "finish": [
        {
            "type": "text",
            "content": ["...Alright, I've memorized it. Now I can remember it anytime. I'll put the charcoal back."]
        }
    ],
    "GAME_OVER_1": [
        {
            "type": "text",
            "content": [
                "When I woke up, I was back in that cold, inorganic solitary cell.",
                "It seems the rehabilitation has been terminated.",
                "They are right behind me.",
            ]
        },
        {
            "type": "pattern", 
            "content": ["終"]
        },
            {
                "type": "text",
                "content": [
                    "Just as in the beginning, I was forced by my own hand to consent to the discharge.",
                    "I know all too well the fate of experimental animals that have finished their roles.",
                ]
            },
    ],
    "GAME_OVER_2": [
        {
            "type": "text",
            "content": [
                "...When I woke up, I was in an unfamiliar facility.",
                "Looking around briefly, without context or purpose, ready-made landscapes simply exist in sequence.",
                "The history of predecessors is engraved on the canvas. I felt as if someone's body heat remained.",
                "Ending 3 LR7: Death of Personnel",
            ]
        }
    ],
    "GAME_CLEAR": [
        {
            "type": "text",
            "content": [
                "When I woke up, I found myself at a dining table, unnervingly pristine.",
                "The difference was the heavy, warm sensation around my neck.",
                "The meaning of the voices that had been noise flows directly into my brain.",
                "It's a much purer, more violent understanding than words.",
            ]
        },
        {
            "type": "pattern", 
            "content": ["得る"]
        },
        {
            "type": "text",
            "content": [
                "<Well done. Congratulations.>",
                "<You have been officially recognized as our obedient, clever, and lovely pet.>",
            ]
        },
        {
            "type": "pattern", 
            "content": ["得る", "得る", "得る", "得る", "得る", "得る", "得る"]
        },
        {
            "type": "text",
            "content": [
                "<Well done! Well done! Well done! Well done! Well done! Well done! Well done!>",
                "My field of vision is filled with words of blessing.",
                "With every letter engraved, my dignity as a human is worn away, and the craving for reward overwrites my entire body.",
                "<That's right. I've even prepared a mate for you.>",
                "What I was shown was something that could no longer be called human.",
                "While retaining traces of a former comrade, it had been turned into an aberration equipped only with functions for their use.",
                "<Let's proceed to the next experiment. Now, let's create a superior pet together.>",
                "A smile naturally escapes me. I was happier than ever before. For the joy of being managed was the future I had been seeking.",
            ]
        },
        {
            "type": "pattern", 
            "content": ["生", "終", "←", "死", "始"]
        },
        {
            "type": "text",
            "content": [
                "Ending 2 LR7: Death of Personality"
            ]
        },
        
    ],
    "GAME_CLEAR_TRUE": [
        {
            "type": "text",
            "content": [
                "When I woke up, I had been transferred to a large room, together with other detainees, to await processing.",
                "I understood their purpose. However, they never understood my silence and will.",
                "What they tried to give was the peace of livestock, and what I guarded to the end was the curse of being human.",
                "Knowing their arrogance, I did not give up on listening. However, they gave up on examining.",
            ]
        }
    ],
    "TRUE_ACTION": [
        {
            "type": "text",
            "content": [
                "<Wildlife that is uncontrollable and retains aggressiveness should be culled immediately.>",
                "We were released from the concrete box called civilization."
                "The flash of light were quieter than expected. Words lost their meaning sooner than expected.",
                "Ending 1 LR7: Death of Humanity"
            ]
        }
    ],
    "TITLE": [
        {
            "type": "text",
            "content": ["Speech Therapy Room LR7"]
        }
    ],
    "RELEASE_MASTER": [
        {
            "type": "text",
            "content": ["As the next subject, [Master], capable of translating from sound to text, has arrived."]
        }
    ],
    "RELEASE_DOCTOR": [
        {
            "type": "text",
            "content": ["Through repeated selective breeding, [Doctor], capable of translating from sound to text and then to vocabulary, was born."]
        }
    ],
    "GAME_END": [
        {
            "type": "text",
            "content": [
                 "How much time has passed since the concrete crumbled and the facility collapsed?",
                 "Crouching in the shadow of warped corrugated iron, I dragged an unopened PET bottle from a parcel tossed carelessly onto the ground.",
                 "There were two dozen and four bottles remaining in the parcel.",
                 "The sound of sand being kicked came from behind. Looking back, a small animal with soft fur was frantically digging a hole.",
                 "\"...Are you alone, too?\"\nThe words spilled from my cracked lips.",
                 "I cannot judge if surviving was a stroke of luck or a detention. We were simply strange compatriots.",
                 "The creature looked up, its gaze piercing me. Its shallow, heavy breaths desperately inhaled the scorched air.",
                 "\"Are you thirsty?\"\nThe sound of PET sealing breaking echoed through the wasteland.",
                 "I lowered the bottle to the animal's eye level and slid it forward with my fingertips, careful not to startle it.",
                 "After a brief silence, the animal closed the distance. The faint sound of water being lapped up began to reach my ears.",
                 "\"It's good, isn't it?\"\nSuddenly, the sound stopped.",
                 "With water dripping from its mouth, its eyes locked onto mine.",
                 "With a single bark, it vanished into the gaps of the rubble.",
                 "A moment later, a howl louder than the first rang out. ...Foolishly, it was only then that I realized my identity with THEM.",
                 "Two dozen and four bottles. At one bottle a day, that was exactly four weeks' worth."
            ]
        }
    ],
}