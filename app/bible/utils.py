from django.db import models


class BibleBookType(models.TextChoices):
    # 구약 - 모세오경 (5권)
    GENESIS = "GENESIS", "창세기"
    EXODUS = "EXODUS", "출애굽기"
    LEVITICUS = "LEVITICUS", "레위기"
    NUMBERS = "NUMBERS", "민수기"
    DEUTERONOMY = "DEUTERONOMY", "신명기"

    # 구약 - 역사서 (12권)
    JOSHUA = "JOSHUA", "여호수아"
    JUDGES = "JUDGES", "사사기"
    RUTH = "RUTH", "룻기"
    ONE_SAMUEL = "1_SAMUEL", "사무엘상"
    TWO_SAMUEL = "2_SAMUEL", "사무엘하"
    ONE_KINGS = "1_KINGS", "열왕기상"
    TWO_KINGS = "2_KINGS", "열왕기하"
    ONE_CHRONICLES = "1_CHRONICLES", "역대상"
    TWO_CHRONICLES = "2_CHRONICLES", "역대하"
    EZRA = "EZRA", "에스라"
    NEHEMIAH = "NEHEMIAH", "느헤미야"
    ESTHER = "ESTHER", "에스더"

    # 구약 - 시가서 (5권)
    JOB = "JOB", "욥기"
    PSALMS = "PSALMS", "시편"
    PROVERBS = "PROVERBS", "잠언"
    ECCLESIASTES = "ECCLESIASTES", "전도서"
    SONG_OF_SONGS = "SONG_OF_SONGS", "아가"

    # 구약 - 대선지서 (5권)
    ISAIAH = "ISAIAH", "이사야"
    JEREMIAH = "JEREMIAH", "예레미야"
    LAMENTATIONS = "LAMENTATIONS", "예레미야애가"
    EZEKIEL = "EZEKIEL", "에스겔"
    DANIEL = "DANIEL", "다니엘"

    # 구약 - 소선지서 (12권)
    HOSEA = "HOSEA", "호세아"
    JOEL = "JOEL", "요엘"
    AMOS = "AMOS", "아모스"
    OBADIAH = "OBADIAH", "오바댜"
    JONAH = "JONAH", "요나"
    MICAH = "MICAH", "미가"
    NAHUM = "NAHUM", "나훔"
    HABAKKUK = "HABAKKUK", "하박국"
    ZEPHANIAH = "ZEPHANIAH", "스바냐"
    HAGGAI = "HAGGAI", "학개"
    ZECHARIAH = "ZECHARIAH", "스가랴"
    MALACHI = "MALACHI", "말라기"

    # 신약 - 복음서 (4권)
    MATTHEW = "MATTHEW", "마태복음"
    MARK = "MARK", "마가복음"
    LUKE = "LUKE", "누가복음"
    JOHN = "JOHN", "요한복음"

    # 신약 - 역사서 (1권)
    ACTS = "ACTS", "사도행전"

    # 신약 - 바울서신 (13권)
    ROMANS = "ROMANS", "로마서"
    ONE_CORINTHIANS = "1_CORINTHIANS", "고린도전서"
    TWO_CORINTHIANS = "2_CORINTHIANS", "고린도후서"
    GALATIANS = "GALATIANS", "갈라디아서"
    EPHESIANS = "EPHESIANS", "에베소서"
    PHILIPPIANS = "PHILIPPIANS", "빌립보서"
    COLOSSIANS = "COLOSSIANS", "골로새서"
    ONE_THESSALONIANS = "1_THESSALONIANS", "데살로니가전서"
    TWO_THESSALONIANS = "2_THESSALONIANS", "데살로니가후서"
    ONE_TIMOTHY = "1_TIMOTHY", "디모데전서"
    TWO_TIMOTHY = "2_TIMOTHY", "디모데후서"
    TITUS = "TITUS", "디도서"
    PHILEMON = "PHILEMON", "빌레몬서"

    # 신약 - 일반서신 (8권)
    HEBREWS = "HEBREWS", "히브리서"
    JAMES = "JAMES", "야고보서"
    ONE_PETER = "1_PETER", "베드로전서"
    TWO_PETER = "2_PETER", "베드로후서"
    ONE_JOHN = "1_JOHN", "요한일서"
    TWO_JOHN = "2_JOHN", "요한이서"
    THREE_JOHN = "3_JOHN", "요한삼서"
    JUDE = "JUDE", "유다서"

    # 신약 - 예언서 (1권)
    REVELATION = "REVELATION", "요한계시록"


# 성경 각 권의 장 수
BIBLE_CHAPTERS = {
    # 구약 - 모세오경 (5권)
    BibleBookType.GENESIS: 50,
    BibleBookType.EXODUS: 40,
    BibleBookType.LEVITICUS: 27,
    BibleBookType.NUMBERS: 36,
    BibleBookType.DEUTERONOMY: 34,
    # 구약 - 역사서 (12권)
    BibleBookType.JOSHUA: 24,
    BibleBookType.JUDGES: 21,
    BibleBookType.RUTH: 4,
    BibleBookType.ONE_SAMUEL: 31,
    BibleBookType.TWO_SAMUEL: 24,
    BibleBookType.ONE_KINGS: 22,
    BibleBookType.TWO_KINGS: 25,
    BibleBookType.ONE_CHRONICLES: 29,
    BibleBookType.TWO_CHRONICLES: 36,
    BibleBookType.EZRA: 10,
    BibleBookType.NEHEMIAH: 13,
    BibleBookType.ESTHER: 10,
    # 구약 - 시가서 (5권)
    BibleBookType.JOB: 42,
    BibleBookType.PSALMS: 150,
    BibleBookType.PROVERBS: 31,
    BibleBookType.ECCLESIASTES: 12,
    BibleBookType.SONG_OF_SONGS: 8,
    # 구약 - 대선지서 (5권)
    BibleBookType.ISAIAH: 66,
    BibleBookType.JEREMIAH: 52,
    BibleBookType.LAMENTATIONS: 5,
    BibleBookType.EZEKIEL: 48,
    BibleBookType.DANIEL: 12,
    # 구약 - 소선지서 (12권)
    BibleBookType.HOSEA: 14,
    BibleBookType.JOEL: 3,
    BibleBookType.AMOS: 9,
    BibleBookType.OBADIAH: 1,
    BibleBookType.JONAH: 4,
    BibleBookType.MICAH: 7,
    BibleBookType.NAHUM: 3,
    BibleBookType.HABAKKUK: 3,
    BibleBookType.ZEPHANIAH: 3,
    BibleBookType.HAGGAI: 2,
    BibleBookType.ZECHARIAH: 14,
    BibleBookType.MALACHI: 4,
    # 신약 - 복음서 (4권)
    BibleBookType.MATTHEW: 28,
    BibleBookType.MARK: 16,
    BibleBookType.LUKE: 24,
    BibleBookType.JOHN: 21,
    # 신약 - 역사서 (1권)
    BibleBookType.ACTS: 28,
    # 신약 - 바울서신 (13권)
    BibleBookType.ROMANS: 16,
    BibleBookType.ONE_CORINTHIANS: 16,
    BibleBookType.TWO_CORINTHIANS: 13,
    BibleBookType.GALATIANS: 6,
    BibleBookType.EPHESIANS: 6,
    BibleBookType.PHILIPPIANS: 4,
    BibleBookType.COLOSSIANS: 4,
    BibleBookType.ONE_THESSALONIANS: 5,
    BibleBookType.TWO_THESSALONIANS: 3,
    BibleBookType.ONE_TIMOTHY: 6,
    BibleBookType.TWO_TIMOTHY: 4,
    BibleBookType.TITUS: 3,
    BibleBookType.PHILEMON: 1,
    # 신약 - 일반서신 (8권)
    BibleBookType.HEBREWS: 13,
    BibleBookType.JAMES: 5,
    BibleBookType.ONE_PETER: 5,
    BibleBookType.TWO_PETER: 3,
    BibleBookType.ONE_JOHN: 5,
    BibleBookType.TWO_JOHN: 1,
    BibleBookType.THREE_JOHN: 1,
    BibleBookType.JUDE: 1,
    # 신약 - 예언서 (1권)
    BibleBookType.REVELATION: 22,
}
