from functools import wraps
from typing import List, Tuple, get_origin, get_args
import inspect


def type_check_decorator(_param=True, _return=True):
    """정적인 타입 체크

    Args:
        _param (bool, optional): 파라미터 체크 여부. Defaults to True.
        _return (bool, optional): 반환값 체크 여부. Defaults to True.
    """
    def wrapper_with_args(func):
        sig = inspect.signature(func)
        params = sig.parameters

        def is_equal_value_and_typehint(value, type_hint) -> bool:
            """Generic 타입을 포함한 변수와 type hint의 비교 함수

            Args:
                value (_type_): 타입을 확인할 변수
                type_hint (_type_): type_hint 값

            Returns:
                bool: 비교 결과
            """
            origin = get_origin(type_hint)
            # isinstance(value, type_hint)
            # print(">>>", value, type_hint, origin, len(get_args(type_hint)), len(origin) if origin else None)
            print(">>>", value, type_hint, origin)
            
            if origin is None:  # Not a generic type
                return isinstance(value, type_hint)
            elif isinstance(value, origin):
                # print("############", isinstance(value, type_hint))
                args = get_args(type_hint)
                # print("<<<", args, len(args), len(value), sep="  --  ")
                if len(args) == 0:  # Generic with no args, e.g. List
                    return True
                elif all(is_equal_value_and_typehint(v, a) for v, a in zip(value, args)):
                # elif (len(args) == len(value) and all(is_equal_value_and_typehint(v, a) for v, a in zip(value, args))) or \
                #      all(is_equal_value_and_typehint(v, args) for v in value):
                    return True
                # elif all(is_equal_value_and_typehint(v, a) for v, a in zip(value, args)):
                # elif all(is_equal_value_and_typehint(v, args) for v in value):
                #     return True
            return False
        
        @wraps(func)
        def wrapper_inner(*args, **kwargs):
            """변수+반환값과 type hint를 비교

            Raises:
                TypeError: 타입이 맞지 않는 경우
            """
            if _param:
                bound_values = sig.bind(*args, **kwargs)
                for name, value in bound_values.arguments.items():
                    print(params[name].annotation)
                    if params[name].annotation is not inspect._empty and \
                    not is_equal_value_and_typehint(value, params[name].annotation):
                        raise TypeError(f"Argument {name}={value} is not of expected type {params[name].annotation}")
            
            result = func(*args, **kwargs)
            if _return and \
                sig.return_annotation is not inspect._empty and \
                not is_equal_value_and_typehint(result, sig.return_annotation):
                raise TypeError(f"Return value {result} is not of expected type {sig.return_annotation}")
            return result

        return wrapper_inner
    return wrapper_with_args

# 데코레이터의 옵션을 다르게 설정하며 테스트 진행
# for each_deco_config in [{}, {"_param":False}, {"_return":False}, {"_param":False, "_return":False}]:
# for each_deco_config in [{"_return":False}]:
#     @type_check_decorator(**each_deco_config)
#     def test_func2(var1:List[str]) -> List[int]:
#         print(var1)
#         return [1]

#     print(f"deco_config::{each_deco_config} - Start!!!")
    
#     test_func2(["1", 2])


for each_deco_config in [{}, {"_param":False}, {"_return":False}, {"_param":False, "_return":False}]:
    try:
        @type_check_decorator(**each_deco_config)
        def test_func(var1:int, var2:str) -> Tuple[int, int]:
            print("var1:", var1 + 10)
            print("var2:", var2)
            
            return [3,3]
        
        @type_check_decorator(**each_deco_config)
        def test_func2(var1:List[str]) -> List[str]:
            print(var1)
            return var1

        print(f"deco_config::{each_deco_config} - Start!!!")
        
        # test_func2(["1", "2"])
        test_func(1, "2")
        # test_func(1, 2)
    except Exception as e:
        print(f"Error...  - {type(e)} - {e}")
    else:
        print(f"End!!!")
    finally:
        print("====================")
