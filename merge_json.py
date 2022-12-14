import json
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


def merge_ann(
    pivot_path, plus_path, PATH="../input/data/ICDAR17_Korean/ufo/", split=False
):
    """
    2개의 ufo type의 annotation json파일을 병합하는 코드입니다.
    pivot json파일에 plus json파일이 갖고 있는 images를 병합한 후 다음 2가지의 경우에 대하여 image 데이터를 제거합니다.
    1. image에 word가 없는 경우
    2. box의 shape이 (4,2)가 아닌 경우 (즉 box가 6각형 8각형 등 제거, 4각형 box만 사용)
    Args:
        pivot_path (str): 병합에 기준이 될 json파일의 이름을 적어주세요.
        plus_path (str): 병합을 할 json파일의 이름을 적어주세요
        PATH (str, optional): json 파일이 존재하는 경로를 적어주세요.
        split (bool): merge한 json 파일을 train과 valid로 분할하는지 여부
    """

    with open(PATH + pivot_path, "r") as f:
        pivot = json.load(f)
    with open(PATH + plus_path, "r") as f:
        plus = json.load(f)

    result = pivot["images"]
    result.update(**plus["images"])

    total = len(result)
    name = sorted(result.keys())
    for na in name:
        word = result[na]["words"].keys()
        if not word:
            del result[na]
        for w in word:
            A = np.array(result[na]["words"][w]["points"])
            if A.shape != (4, 2):
                del result[na]
                break
    print("삭제된 이미지", total - len(result))

    if split:
        s = pd.Series(result)
        training_data, valid_data = [
            i.to_dict() for i in train_test_split(s, train_size=0.8, random_state=2022)
        ]
        pivot["images"] = training_data
        with open(PATH + "my_ann_train.json", "w") as outfile:
            json.dump(pivot, outfile)
        pivot["images"] = valid_data
        with open(PATH + "my_ann_valid.json", "w") as outfile:
            json.dump(pivot, outfile)

    else:
        pivot["images"] = result
        with open(PATH + "my_ann.json", "w") as outfile:
            json.dump(pivot, outfile)


if __name__ == "__main__":
    merge_ann("train.json", "annotation.json")
