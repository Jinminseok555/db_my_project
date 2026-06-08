from abc import ABC, abstractmethod
import pandas as pd

# =========================================================================
# 1. 데이터베이스 연결 인터페이스 (기본)
# =========================================================================
class IDatabaseManager(ABC):
    @abstractmethod
    def get_connection(self): ...
    @abstractmethod
    def close(self) -> None: ...

# =========================================================================
# 2. 공통 레포지토리 (모든 테이블이 상속받음)
# =========================================================================
class IRepository(ABC):
    def __init__(self, db: IDatabaseManager):
        self._con = db.get_connection()

    @abstractmethod
    def create_table(self) -> None: ...
    @abstractmethod
    def count(self) -> int: ...

# =========================================================================
# 3. 테이블별 확장 인터페이스
# =========================================================================

# 8.1 식재료 목록 및 상세 조회
class IIngredientRepository(IRepository):
    @abstractmethod
    def find_all(self) -> pd.DataFrame: ...
    @abstractmethod
    def find_by_id(self, id: int) -> pd.DataFrame: ...

# 8.2 초간단 자취 레시피 정보
class IRecipeRepository(IRepository):
    @abstractmethod
    def find_all(self) -> pd.DataFrame: ...
    @abstractmethod
    def find_by_id(self, recipe_id: int) -> pd.DataFrame: ...

# 8.3 레시피별 필요 재료 매핑
class IRecipeMappingRepository(IRepository):
    @abstractmethod
    def find_by_recipe(self, recipe_id: int) -> pd.DataFrame: ...

# 8.4 대학생 상황별 맞춤 매칭
class IConditionFilterRepository(IRepository):
    @abstractmethod
    def find_by_condition(self, condition: str) -> pd.DataFrame: ...

# 8.5 냉장고 해먹기 (소모/갱신)
class IFridgeStockRepository(IRepository):
    @abstractmethod
    def update_stock(self, ingredient_id: int, qty: int) -> None: ...
    @abstractmethod
    def find_inventory(self) -> pd.DataFrame: ...

# 8.6 Join 정보 인터페이스 (종합 매칭)
class ICookingMatcherRepository(ABC):
    """JOIN 연산은 데이터 연결이 필요하므로 일반 Repository와 분리 또는 확장"""
    def __init__(self, db: IDatabaseManager):
        self.con = db.get_connection()

    @abstractmethod
    def find_cookable_recipes(self) -> pd.DataFrame: ...