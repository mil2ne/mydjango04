# Generated by Django 4.2.13 on 2024-06-05 21:45

import csv
import itertools
from typing import Dict, Iterator, Tuple

from django.db import migrations


CSV_PATH = "shop/assets/zipcode_db/20231205/서울특별시.txt"


def get_code_and_name_from_csv(zipcode_csv_path: str) -> Iterator[Tuple[str, str]]:
    """CSV 파일에서 우편번호, 시도, 시군구, 도로명을 읽어서, 우편번호와 주소를 생성합니다.
    :param zipcode_csv_path: 우편번호 CSV 파일 경로
    :return: 우편번호, 주소 튜플을 생성(yield)합니다.
    """

    with open(zipcode_csv_path, "rt", encoding="utf-8-sig") as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter="|")

        row: Dict
        for row in csv_reader:
            code = row["우편번호"]
            name = "{시도} {시군구} {도로명}".format(**row)
            yield code, name


def get_chunks(iterable: Iterator, chunk_size: int = 100) -> Iterator:
    """주어진 iterable 객체를 chunk_size 크기의 청크(chunk, 연속적인 데이터의 일부)로 나누는 제너레이터 함수입니다.
    이 함수는 Generator Expression을 활용하여, 주어진 iterable을 지정된 크기의 청크로 나눕니다.
    각 청크는 iterable의 연속적인 요소들로 구성됩니다.
    :param iterable: 청크로 나눌 iterable 객체
    :param chunk_size: 청크의 크기, 기본값은 100
    :return: 지정된 크기의 청크를 순차적으로 생성(yield)하는 제너레이터
    """

    # iterable이 iterator가 아니면, iterator로 변환
    iterator = iterable if hasattr(iterable, "__next__") else iter(iterable)

    # iterator에서는 값을 꺼내기 전에는 남은 값이 있는 지 알 수 없기 때문에 먼저 값을 하나 꺼냅니다.
    # iterator에서 첫 번째 값을 꺼내고, 남은 값들을 chunk_size - 1만큼 더 꺼내어 yield
    # 첫 번째 값을 꺼낼 때 StopIteration 예외가 발생하면, 반복 종료
    for first in iterator:
        # 첫번째 값과 남은 값들을 연결(chain)하여 yield
        yield itertools.chain([first], itertools.islice(iterator, chunk_size - 1))


def add_zipcode_data(apps, schema_editor):
    ZipCode = apps.get_model("shop", "ZipCode")

    # Generator Expression
    # - 리스트로 변환하기보다 제네레이터 표현식을 사용하면
    # 메모리를 아끼고 보다 빠르게 작업을 시작할 수 있습니다.
    zipcode_list = (
        ZipCode(code=code, name=name)
        for code, name in get_code_and_name_from_csv(CSV_PATH)
    )

    # 배치 크기 단위로 insert 쿼리를 모아서 실행
    # ZipCode.objects.bulk_create(zipcode_list, batch_size=1000)
    for chunks in get_chunks(zipcode_list, chunk_size=1000):
        chunks_list = list(chunks)
        print("chunk_size:", len(list(chunks_list)))
        ZipCode.objects.bulk_create(chunks_list)


def remove_zipcode_data(apps, schema_editor):
    ZipCode = apps.get_model("shop", "ZipCode")
    ZipCode.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [migrations.RunPython(add_zipcode_data, remove_zipcode_data)]
