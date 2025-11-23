"""
データベース整合性検証スクリプト

以下を検証:
1. 外部キー制約の存在確認
2. 孤児レコードの検出
3. リレーションシップの双方向性
4. 一意制約の検証
5. チェック制約の検証
6. インデックスの存在確認
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal, engine
from app.models import Base

try:
    import yaml
except ImportError:
    print("⚠️  Warning: pyyaml not installed. Run: pip install pyyaml")
    yaml = None


class DatabaseIntegrityValidator:
    """データベース整合性を検証するクラス"""
    
    def __init__(self, session: Session):
        self.session = session
        self.inspector = inspect(engine)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.schema_constraints = None
        
        # schema-constraints.yml を読み込む（存在する場合）
        if yaml:
            constraints_path = Path(__file__).parent.parent.parent / "openspec/specs/database/schema-constraints.yml"
            if constraints_path.exists():
                with open(constraints_path) as f:
                    self.schema_constraints = yaml.safe_load(f)
    
    def validate_all(self) -> bool:
        """すべての検証を実行"""
        print("🔍 データベース整合性検証を開始...")
        print()
        
        if self.schema_constraints:
            self.validate_foreign_keys()
        else:
            print("⚠️  schema-constraints.yml が見つかりません。外部キー検証をスキップします。")
        
        self.validate_orphan_records()
        
        if self.schema_constraints:
            self.validate_unique_constraints()
            self.validate_check_constraints()
            self.validate_indexes()
        
        self.validate_relationship_bidirectionality()
        
        # 結果表示
        print("\n" + "="*70)
        if self.errors:
            print(f"❌ {len(self.errors)} 個のエラーが見つかりました:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        else:
            print("✅ エラーはありませんでした")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} 個の警告があります:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        print("="*70)
        
        return len(self.errors) == 0
    
    def validate_foreign_keys(self):
        """外部キー制約の検証"""
        print("📋 外部キー制約の検証...")
        
        if not self.schema_constraints or 'foreign_key_rules' not in self.schema_constraints:
            print("  ⚠️  外部キー制約ルールが定義されていません")
            return
        
        rules = self.schema_constraints['foreign_key_rules']
        checked_count = 0
        
        # CASCADE制約の検証
        if 'cascade_deletes' in rules:
            for rule in rules['cascade_deletes']:
                parent = rule['parent']
                for child_item in rule['children']:
                    if isinstance(child_item, dict):
                        child = child_item.get('table')
                        column = child_item.get('column')
                    else:
                        child = child_item
                        # テーブル名から推測（例: tenants -> tenant_id）
                        column = f"{parent.rstrip('s')}_id"
                    
                    self._check_foreign_key_exists(child, column, parent, 'CASCADE')
                    checked_count += 1
        
        # SET NULL制約の検証
        if 'set_null_on_delete' in rules:
            for rule in rules['set_null_on_delete']:
                parent = rule['parent']
                for child_ref in rule['children']:
                    if '.' in child_ref:
                        child, column = child_ref.split('.')
                        self._check_foreign_key_exists(child, column, parent, 'SET NULL')
                        checked_count += 1
        
        print(f"  ✓ {checked_count} 個の外部キー制約を検証しました\n")
    
    def _check_foreign_key_exists(self, child_table: str, column: str, parent_table: str, on_delete: str):
        """特定の外部キー制約が存在するか確認"""
        try:
            fks = self.inspector.get_foreign_keys(child_table)
        except Exception as e:
            self.warnings.append(f"テーブル {child_table} の外部キー情報を取得できませんでした: {e}")
            return
        
        found = False
        for fk in fks:
            if column in fk['constrained_columns'] and fk['referred_table'] == parent_table:
                found = True
                # ondelete動作の確認
                actual_ondelete = fk.get('ondelete', 'NO ACTION')
                if actual_ondelete and actual_ondelete != on_delete:
                    self.errors.append(
                        f"{child_table}.{column} -> {parent_table}: "
                        f"期待: ondelete={on_delete}, 実際: ondelete={actual_ondelete}"
                    )
                break
        
        if not found:
            self.errors.append(
                f"{child_table}.{column} -> {parent_table} の外部キー制約が存在しません"
            )
    
    def validate_orphan_records(self):
        """孤児レコードの検出"""
        print("🔍 孤児レコードの検出...")
        
        orphan_checks = [
            # (子テーブル, 外部キーカラム, 親テーブル, 親ID)
            ('users', 'tenant_id', 'tenants', 'id'),
            ('assessments', 'tenant_id', 'tenants', 'id'),
            ('leads', 'tenant_id', 'tenants', 'id'),
            ('questions', 'assessment_id', 'assessments', 'id'),
            ('answers', 'response_id', 'responses', 'id'),
            ('answers', 'question_id', 'questions', 'id'),
            ('question_options', 'question_id', 'questions', 'id'),
            ('qr_code_scans', 'qr_code_id', 'qr_codes', 'id'),
        ]
        
        total_orphans = 0
        for child_table, fk_column, parent_table, parent_id in orphan_checks:
            try:
                query = f"""
                    SELECT COUNT(*) 
                    FROM {child_table} 
                    WHERE {fk_column} IS NOT NULL 
                    AND {fk_column} NOT IN (SELECT {parent_id} FROM {parent_table})
                """
                result = self.session.execute(text(query))
                orphan_count = result.scalar()
                
                if orphan_count > 0:
                    self.errors.append(
                        f"{child_table} に {orphan_count} 件の孤児レコードが存在します "
                        f"(参照先: {parent_table}.{parent_id})"
                    )
                    total_orphans += orphan_count
            except Exception as e:
                self.warnings.append(f"{child_table} の孤児レコードチェック失敗: {e}")
        
        if total_orphans == 0:
            print(f"  ✓ 孤児レコードは検出されませんでした\n")
        else:
            print(f"  ✗ 合計 {total_orphans} 件の孤児レコードが検出されました\n")
    
    def validate_unique_constraints(self):
        """一意制約の検証"""
        print("🔑 一意制約の検証...")
        
        if not self.schema_constraints or 'unique_constraints' not in self.schema_constraints:
            print("  ⚠️  一意制約ルールが定義されていません\n")
            return
        
        checked_count = 0
        for constraint in self.schema_constraints['unique_constraints']:
            table = constraint['table']
            columns = constraint['columns']
            
            try:
                # 重複チェック
                cols_str = ', '.join(columns)
                query = f"""
                    SELECT {cols_str}, COUNT(*) as cnt
                    FROM {table}
                    GROUP BY {cols_str}
                    HAVING COUNT(*) > 1
                """
                result = self.session.execute(text(query))
                duplicates = result.fetchall()
                
                if duplicates:
                    self.errors.append(
                        f"{table} の {cols_str} に {len(duplicates)} 件の重複があります"
                    )
                checked_count += 1
            except Exception as e:
                self.warnings.append(f"{table} の一意制約チェック失敗: {e}")
        
        print(f"  ✓ {checked_count} 個の一意制約を検証しました\n")
    
    def validate_check_constraints(self):
        """チェック制約の検証"""
        print("✔️  チェック制約の検証...")
        
        if not self.schema_constraints or 'check_constraints' not in self.schema_constraints:
            print("  ⚠️  チェック制約ルールが定義されていません\n")
            return
        
        checked_count = 0
        for constraint in self.schema_constraints['check_constraints']:
            table = constraint['table']
            expression = constraint['expression']
            constraint_name = constraint.get('constraint', 'unknown')
            
            try:
                # 制約違反のレコードを検索
                query = f"SELECT COUNT(*) FROM {table} WHERE NOT ({expression})"
                result = self.session.execute(text(query))
                violations = result.scalar()
                
                if violations > 0:
                    self.errors.append(
                        f"{table} で {violations} 件のチェック制約違反: {constraint_name}"
                    )
                checked_count += 1
            except Exception as e:
                self.warnings.append(f"{table}.{constraint_name} のチェック失敗: {e}")
        
        print(f"  ✓ {checked_count} 個のチェック制約を検証しました\n")
    
    def validate_indexes(self):
        """インデックスの存在確認"""
        print("📇 インデックスの検証...")
        
        if not self.schema_constraints or 'indexes' not in self.schema_constraints:
            print("  ⚠️  インデックス定義が見つかりません\n")
            return
        
        checked_count = 0
        for idx_type in ['performance', 'uniqueness']:
            if idx_type not in self.schema_constraints['indexes']:
                continue
            
            for idx in self.schema_constraints['indexes'][idx_type]:
                table = idx['table']
                columns = idx['columns']
                
                try:
                    # インデックスの存在確認
                    indexes = self.inspector.get_indexes(table)
                    
                    found = False
                    for db_idx in indexes:
                        if set(db_idx['column_names']) == set(columns):
                            found = True
                            break
                    
                    if not found:
                        self.warnings.append(
                            f"{table} に推奨インデックスが存在しません: {', '.join(columns)}"
                        )
                    checked_count += 1
                except Exception as e:
                    self.warnings.append(f"{table} のインデックスチェック失敗: {e}")
        
        print(f"  ✓ {checked_count} 個のインデックスを検証しました\n")
    
    def validate_relationship_bidirectionality(self):
        """SQLAlchemyリレーションシップの双方向性検証"""
        print("🔗 リレーションシップの双方向性検証...")
        
        checked_count = 0
        # すべてのモデルクラスを取得
        for mapper in Base.registry.mappers:
            model_class = mapper.class_
            
            # リレーションシップを確認
            for rel in mapper.relationships:
                # back_populatesが設定されているか
                if rel.back_populates is None and rel.backref is None:
                    self.warnings.append(
                        f"{model_class.__name__}.{rel.key} に back_populates または backref が設定されていません"
                    )
                checked_count += 1
        
        print(f"  ✓ {checked_count} 個のリレーションシップを検証しました\n")


def main():
    """メイン処理"""
    print("="*70)
    print("  Database Integrity Validator")
    print("="*70)
    print()
    
    session = SessionLocal()
    try:
        validator = DatabaseIntegrityValidator(session)
        success = validator.validate_all()
        
        if success:
            print("\n✅ データベース整合性検証が完了しました。問題ありません。")
            sys.exit(0)
        else:
            print("\n❌ データベース整合性に問題があります。上記のエラーを修正してください。")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 検証中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
