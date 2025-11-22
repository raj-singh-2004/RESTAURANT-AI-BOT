"""
Enhanced Menu Search System
Improved semantic search with fuzzy matching and better ranking
"""

import json
import os
import time
import gc
import shutil
from typing import List, Dict, Optional, Tuple
import re
from difflib import SequenceMatcher

import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np


class ImprovedMenuSearchSystem:
    """Enhanced search with better understanding and ranking"""

    def __init__(self, db_path: str = "./chroma_db"):
        """Initialize with improved model and systems"""
        
        self.client: Optional[object] = None
        self.collection = None
        self.db_path = db_path
        
        # Use a better model for embeddings
        self.model_name = "sentence-transformers/all-mpnet-base-v2"

        print(f"Initializing Enhanced Menu Search System...")
        print(f"  Database: {db_path}")
        print(f"  Model: {self.model_name}")
        
        # Load embedding model
        print("  Loading model...")
        self.model = SentenceTransformer(self.model_name)
        test_embedding = self.model.encode("test", convert_to_numpy=True)
        self.embedding_dim = len(test_embedding)
        print(f"  Model dimension: {self.embedding_dim}")
        
        # Initialize query enhancement system
        self._init_query_system()
        
        print("✔ Ready\n")

    def _init_query_system(self):
        """Initialize comprehensive query enhancement"""
        
        # Expanded synonyms and contextual expansions
        self.query_expansions = {
            # Dietary terms
            'vegetarian': 'vegetarian veg veggie plant-based no-meat vegetables herbivore meatless',
            'veg': 'vegetarian veg veggie plant-based no-meat vegetables',
            'non-veg': 'non-vegetarian meat chicken mutton fish prawns seafood carnivore',
            'vegan': 'vegan plant-based dairy-free no-milk no-cheese no-animal purely-vegetable',
            'egg': 'egg eggs omelette scrambled anda boiled',
            
            # Taste profiles
            'spicy': 'spicy hot chilli pepper schezwan fiery pungent tikha masala burning',
            'sweet': 'sweet dessert sugar honey chocolate mithai halwa syrup',
            'tangy': 'tangy sour lemon tamarind khatta imli acidic',
            'crispy': 'crispy fried crunchy crisp pakora bhajiya tempura golden',
            'creamy': 'creamy cream cheese malai korma rich smooth velvety',
            'mild': 'mild light simple plain basic bland gentle',
            'savory': 'savory salty umami tasty flavorful delicious',
            
            # Price indicators
            'cheap': 'cheap affordable budget economical inexpensive low-cost value-for-money pocket-friendly',
            'expensive': 'expensive premium costly luxury high-end special fancy',
            'affordable': 'affordable reasonable moderate budget-friendly fair-priced',
            
            # Meal times
            'breakfast': 'breakfast morning tiffin nashta early-meal idli dosa upma poha',
            'lunch': 'lunch afternoon meal thali combo daytime midday',
            'dinner': 'dinner evening supper night-meal main-course',
            'snacks': 'snacks snack teatime evening-snack munchies namkeen quick-bite',
            
            # Common ingredients
            'paneer': 'paneer cottage-cheese indian-cheese dairy cheese-cubes',
            'chicken': 'chicken murgh poultry white-meat',
            'rice': 'rice chawal pulao biryani fried-rice steamed-rice',
            'noodles': 'noodles chowmein hakka pasta spaghetti',
            'bread': 'bread roti naan chapati paratha kulcha',
            'potato': 'potato aloo batata potatoes tater',
            'cheese': 'cheese paneer cottage-cheese dairy mozzarella',
            
            # Categories/Cuisines
            'chinese': 'chinese oriental asian chowmein noodles manchurian schezwan hakka canton',
            'indian': 'indian desi traditional bhartiya hindustan masala curry',
            'south indian': 'south-indian southindian dosa idli vada uttapam sambhar rasam',
            'north indian': 'north-indian northindian punjabi tandoori naan paneer dal',
            'italian': 'italian pasta pizza spaghetti lasagna continental european',
            'beverages': 'beverages drinks tea coffee juice shake lassi mocktail beverage',
            'drinks': 'drinks beverages tea coffee juice shake soda liquid refreshment',
            
            # Cooking styles
            'fried': 'fried deep-fried tawa-fried pan-fried bhuna crispy crunchy',
            'grilled': 'grilled tandoori roasted barbecue bbq charcoal smoked',
            'steamed': 'steamed boiled healthy light oil-free gentle',
            'baked': 'baked oven-baked roasted',
            
            # Health related
            'healthy': 'healthy diet low-calorie nutritious wholesome light salad fit',
            'heavy': 'heavy filling rich substantial hearty satisfying',
            
            # Additional food terms
            'sandwich': 'sandwich burger bread toast grilled',
            'soup': 'soup broth liquid hot warm',
            'salad': 'salad fresh vegetables healthy greens raw',
        }
        
        # Fuzzy matching threshold
        self.fuzzy_threshold = 0.6
        
        # Price extraction patterns
        self.price_patterns = [
            (r'under\s+(\d+)', lambda x: float(x)),
            (r'below\s+(\d+)', lambda x: float(x)),
            (r'less\s+than\s+(\d+)', lambda x: float(x)),
            (r'cheaper\s+than\s+(\d+)', lambda x: float(x)),
            (r'within\s+(\d+)', lambda x: float(x)),
            (r'max\s+(\d+)', lambda x: float(x)),
            (r'maximum\s+(\d+)', lambda x: float(x)),
            (r'upto\s+(\d+)', lambda x: float(x)),
            (r'around\s+(\d+)', lambda x: float(x) * 1.2),
        ]

    def ensure_client(self):
        """Create chromadb client if needed"""
        if self.client is not None:
            return

        os.makedirs(self.db_path, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
        except:
            self.client = chromadb.Client(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.db_path
            )

    def create_database(self, menu_json_path: str):
        """Create enhanced database with rich embeddings"""
        
        self.ensure_client()

        # Delete existing collection
        try:
            self.client.delete_collection("menu_items")
        except:
            pass

        # Create new collection
        self.collection = self.client.create_collection(name="menu_items")

        # Load JSON
        with open(menu_json_path, 'r', encoding='utf-8') as f:
            items = json.load(f)

        print(f"Creating enhanced database with {len(items)} items...")

        ids = []
        metadatas = []
        embeddings = []
        documents = []

        for i, item in enumerate(items):
            item_id = str(item.get('id', i + 1))
            ids.append(item_id)
            
            # Rich metadata
            metadata = {
                "name": item.get('name', ''),
                "price": float(item.get('price', 0)),
                "category": item.get('category', 'General'),
                "is_vegetarian": bool(item.get('is_vegetarian', False)),
                "is_vegan": bool(item.get('is_vegan', False)),
                "contains_egg": bool(item.get('contains_egg', False)),
            }
            
            # Add optional fields
            for field in ['cuisine_type', 'spice_level', 'description']:
                if field in item:
                    metadata[field] = item[field]
            
            # Store lists as JSON strings
            for field in ['ingredients', 'search_keywords', 'dietary_tags']:
                if field in item:
                    metadata[field] = json.dumps(item[field])
            
            metadatas.append(metadata)
            
            # Create comprehensive searchable document with strategic weighting
            doc_parts = []
            
            # Name (most important - triple weight)
            name = item.get('name', '')
            doc_parts.extend([name] * 3)
            
            # Description (double weight)
            if 'description' in item:
                doc_parts.extend([item['description']] * 2)
            
            # Category and cuisine (double weight)
            category = item.get('category', '')
            cuisine = item.get('cuisine_type', '')
            doc_parts.extend([category, category, cuisine, cuisine])
            
            # Ingredients (triple weight - very important for search)
            if 'ingredients' in item:
                ingredients_text = ' '.join(item['ingredients'])
                doc_parts.extend([ingredients_text] * 3)
            
            # Keywords (double weight)
            if 'search_keywords' in item:
                keywords_text = ' '.join(item['search_keywords'])
                doc_parts.extend([keywords_text] * 2)
            
            # Dietary information (searchable, double weight)
            dietary_terms = []
            if item.get('is_vegetarian'):
                dietary_terms.append('vegetarian veg plant-based meatless')
            if item.get('is_vegan'):
                dietary_terms.append('vegan dairy-free plant-based')
            if item.get('contains_egg'):
                dietary_terms.append('egg eggs contains-egg eggetarian')
            if not item.get('is_vegetarian'):
                dietary_terms.append('non-vegetarian meat non-veg')
            
            if dietary_terms:
                doc_parts.extend(dietary_terms * 2)
            
            # Spice level
            if 'spice_level' in item:
                spice_text = f"{item['spice_level']} spice"
                doc_parts.append(spice_text)
            
            # Price range terms
            price = item.get('price', 0)
            if price < 50:
                doc_parts.append('cheap budget affordable economical')
            elif price < 100:
                doc_parts.append('moderate reasonable')
            else:
                doc_parts.append('premium expensive')
            
            # Combine all parts
            full_document = ' '.join(doc_parts)
            documents.append(full_document)
        
        # Generate embeddings in batches
        batch_size = 32
        print("Generating embeddings...")
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_embeddings = self.model.encode(
                batch_docs,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            embeddings.extend(batch_embeddings.tolist())
            
            if (i // batch_size + 1) % 10 == 0:
                print(f"  Processed {min(i+batch_size, len(documents))}/{len(documents)} items")
        
        # Add to collection
        print("Adding to database...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        print(f"✔ Database created with {len(items)} items")

    def load_database(self) -> bool:
        """Load existing database"""
        
        self.ensure_client()
        
        try:
            self.collection = self.client.get_collection("menu_items")
            count = self.collection.count()
            
            if count > 0:
                print(f"✔ Loaded database with {count} items")
                return True
            else:
                return False
        except:
            return False

    def enhance_query(self, query: str) -> str:
        """Enhance query with synonyms and expansions"""
        
        query_lower = query.lower()
        words = query_lower.split()
        
        enhanced_terms = [query_lower]  # Keep original
        
        # Expand known terms
        for word in words:
            if word in self.query_expansions:
                enhanced_terms.append(self.query_expansions[word])
        
        # Add partial matches for common food terms
        food_terms = ['paneer', 'chicken', 'rice', 'noodles', 'dosa', 'idli', 
                     'pasta', 'burger', 'sandwich', 'tea', 'coffee']
        for term in food_terms:
            if term in query_lower and term not in words:
                enhanced_terms.append(term)
        
        # Combine all enhanced terms
        enhanced_query = ' '.join(enhanced_terms)
        
        return enhanced_query

    def fuzzy_match_score(self, query: str, text: str) -> float:
        """Calculate fuzzy matching score between query and text"""
        
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Exact substring match
        if query_lower in text_lower:
            return 1.0
        
        # Word-level fuzzy matching
        query_words = query_lower.split()
        text_words = text_lower.split()
        
        max_score = 0.0
        for q_word in query_words:
            for t_word in text_words:
                score = SequenceMatcher(None, q_word, t_word).ratio()
                max_score = max(max_score, score)
        
        return max_score

    def search(
        self,
        query: str,
        top_k: int = 5,
        max_price: Optional[float] = None,
        vegetarian_only: bool = False,
        vegan_only: bool = False,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Enhanced search with multiple strategies"""
        
        if not self.collection:
            if not self.load_database():
                return []
        
        # Enhance query
        enhanced_query = self.enhance_query(query)
        
        # Generate query embedding
        query_embedding = self.model.encode(enhanced_query, convert_to_numpy=True)
        
        # Build filters
        where_filter = {}
        
        if vegetarian_only:
            where_filter["is_vegetarian"] = True
        
        if vegan_only:
            where_filter["is_vegan"] = True
        
        if category:
            where_filter["category"] = category
        
        # Perform semantic search (get more results for reranking)
        search_k = min(top_k * 3, 50)  # Get 3x results for reranking
        
        try:
            if where_filter:
                results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=search_k,
                    where=where_filter
                )
            else:
                results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=search_k
                )
        except Exception as e:
            print(f"Search error: {e}")
            return []
        
        # Post-process and rerank results
        reranked_results = self._rerank_results(
            query=query,
            results=results,
            max_price=max_price,
            top_k=top_k
        )
        
        return reranked_results

    def _rerank_results(
        self,
        query: str,
        results: Dict,
        max_price: Optional[float],
        top_k: int
    ) -> List[Dict]:
        """Advanced reranking with multiple signals"""
        
        ids_list = results.get('ids', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0] if 'distances' in results else None
        
        if not ids_list:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        formatted = []
        
        for i, item_id in enumerate(ids_list):
            metadata = metas[i] if i < len(metas) else {}
            
            # Parse JSON fields
            for field in ['ingredients', 'search_keywords', 'dietary_tags']:
                if field in metadata and isinstance(metadata[field], str):
                    try:
                        metadata[field] = json.loads(metadata[field])
                    except:
                        metadata[field] = []
            
            # Apply price filter
            price = metadata.get('price', 0)
            if max_price and price > max_price:
                continue
            
            # Base similarity score from embedding
            base_similarity = 1.0
            if distances and i < len(distances):
                base_similarity = max(0, 1.0 - distances[i])
            
            # Calculate comprehensive boost
            boost = self._calculate_boost(
                metadata=metadata,
                query=query,
                query_lower=query_lower,
                query_words=query_words
            )
            
            # Calculate fuzzy match bonus
            name = metadata.get('name', '')
            fuzzy_score = self.fuzzy_match_score(query, name)
            if fuzzy_score > self.fuzzy_threshold:
                boost *= (1 + fuzzy_score * 0.3)
            
            # Final score
            final_score = base_similarity * boost
            
            formatted.append({
                'id': item_id,
                'metadata': metadata,
                'score': final_score,
                'base_similarity': base_similarity,
                'boost_factor': boost,
                'fuzzy_match': fuzzy_score
            })
        
        # Sort by final score
        formatted.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top k
        return formatted[:top_k]

    def _calculate_boost(
        self,
        metadata: Dict,
        query: str,
        query_lower: str,
        query_words: set[str]
    ) -> float:
        """Calculate comprehensive boost factor"""
        
        boost = 1.0
        name = metadata.get('name', '')
        name_lower = name.lower()
        
        # 1. Exact name match (very strong)
        if query_lower == name_lower:
            boost *= 2.0
        
        # 2. Query is substring of name
        if query_lower in name_lower:
            boost *= 1.5
        
        # 3. Name starts with query
        if name_lower.startswith(query_lower):
            boost *= 1.4
        
        # 4. Word overlap in name
        name_words = set(name_lower.split())
        word_overlap = len(query_words & name_words)
        if word_overlap > 0:
            boost *= (1 + 0.2 * word_overlap)
        
        # 5. Ingredient matching (strong signal)
        ingredients = metadata.get('ingredients', [])
        if ingredients:
            ingredient_matches = 0
            for ing in ingredients:
                ing_lower = ing.lower()
                # Check if any query word is in ingredient
                if any(word in ing_lower for word in query_words if len(word) > 2):
                    ingredient_matches += 1
                # Check if ingredient is in query
                if ing_lower in query_lower:
                    ingredient_matches += 1
            
            if ingredient_matches > 0:
                boost *= (1 + 0.15 * min(ingredient_matches, 3))
        
        # 6. Category relevance
        category = metadata.get('category', '').lower()
        if category and any(word in category for word in query_words):
            boost *= 1.25
        
        # 7. Cuisine type match
        cuisine = metadata.get('cuisine_type', '').lower()
        if cuisine and any(word in cuisine for word in query_words):
            boost *= 1.2
        
        # 8. Price preferences
        price = metadata.get('price', 0)
        
        price_keywords = {
            'cheap': (0, 50),
            'budget': (0, 60),
            'affordable': (0, 80),
            'moderate': (50, 120),
            'expensive': (120, 500),
            'premium': (150, 500)
        }
        
        for keyword, (min_p, max_p) in price_keywords.items():
            if keyword in query_lower:
                if min_p <= price <= max_p:
                    boost *= 1.4
                    break
        
        # 9. Dietary preferences (strong signal)
        dietary_boosts = {
            'veg': ('is_vegetarian', True, 1.3),
            'vegetarian': ('is_vegetarian', True, 1.3),
            'non-veg': ('is_vegetarian', False, 1.3),
            'non vegetarian': ('is_vegetarian', False, 1.3),
            'vegan': ('is_vegan', True, 1.4),
            'egg': ('contains_egg', True, 1.3),
        }
        
        for keyword, (field, expected_value, boost_factor) in dietary_boosts.items():
            if keyword in query_lower:
                if metadata.get(field) == expected_value:
                    boost *= boost_factor
                    break
        
        # 10. Spice level matching
        spice_level = metadata.get('spice_level', 'mild')
        spice_keywords = {
            'spicy': 'hot',
            'hot': 'hot',
            'mild': 'mild',
            'medium': 'medium'
        }
        
        for keyword, expected_level in spice_keywords.items():
            if keyword in query_lower and spice_level == expected_level:
                boost *= 1.25
                break
        
        # 11. Keywords matching
        keywords = metadata.get('search_keywords', [])
        if keywords:
            keyword_matches = sum(1 for kw in keywords 
                                 if any(word in str(kw).lower() for word in query_words if len(word) > 2))
            if keyword_matches > 0:
                boost *= (1 + 0.1 * min(keyword_matches, 3))
        
        # 12. Cooking style matching
        cooking_styles = ['fried', 'grilled', 'steamed', 'baked', 'roasted']
        for style in cooking_styles:
            if style in query_lower and style in name_lower:
                boost *= 1.2
                break
        
        # 13. Meal time relevance
        meal_times = {
            'breakfast': ['breakfast', 'morning', 'idli', 'dosa', 'upma', 'poha'],
            'lunch': ['lunch', 'thali', 'meal', 'rice'],
            'dinner': ['dinner', 'evening', 'meal'],
            'snack': ['snack', 'teatime', 'evening']
        }
        
        for meal_keyword, meal_indicators in meal_times.items():
            if meal_keyword in query_lower:
                if any(indicator in name_lower or indicator in category 
                      for indicator in meal_indicators):
                    boost *= 1.2
                    break
        
        return boost

    def close(self):
        """Clean shutdown"""
        try:
            if self.collection and hasattr(self.collection, "persist"):
                self.collection.persist()
        except:
            pass
        
        try:
            if self.client:
                if hasattr(self.client, "persist"):
                    self.client.persist()
                if hasattr(self.client, "close"):
                    self.client.close()
        except:
            pass
        
        gc.collect()
        time.sleep(0.05)


def main():
    """Test the improved search system"""
    import sys
    
    # Find menu JSON
    paths = ["menu_structured.json", "data/menu_structured.json", "./data/menu_structured.json"]
    menu_path = next((p for p in paths if os.path.exists(p)), None)
    
    if not menu_path:
        print("✖ Menu JSON not found!")
        print("Please run menu_extractor first to create menu_structured.json")
        return
    
    # Database path
    db_path = os.path.join(os.path.dirname(menu_path) or ".", "chroma_db")
    
    # Recreate if requested
    if '--recreate' in sys.argv:
        if os.path.exists(db_path):
            print("Removing old database...")
            shutil.rmtree(db_path)
    
    # Create search system
    search = ImprovedMenuSearchSystem(db_path=db_path)
    
    # Load or create database
    if not search.load_database():
        print("Creating new database...")
        search.create_database(menu_path)
    
    # Test searches
    print("\n" + "="*60)
    print("ENHANCED SEARCH TESTING")
    print("="*60)
    
    test_queries = [
        "vegetarian under 100",
        "spicy chinese",
        "breakfast items",
        "cheap snacks",
        "paneer",
        "something sweet",
        "healthy options",
        "fried rice",
        "dosa",
        "coffee"
    ]
    
    print("\nRunning test searches:\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 40)
        
        results = search.search(query, top_k=3)
        
        if results:
            for r in results:
                m = r['metadata']
                print(f"  {m['name']:<25} ₹{m['price']:<6} Score: {r['score']:.3f}")
                
                # Show matching details
                details = []
                if r.get('fuzzy_match', 0) > 0.6:
                    details.append(f"Fuzzy: {r['fuzzy_match']:.2f}")
                if m.get('is_vegetarian'):
                    details.append("🌱")
                if m.get('ingredients'):
                    details.append(f"Ingredients: {', '.join(m['ingredients'][:2])}")
                
                if details:
                    print(f"    {' | '.join(details)}")
        else:
            print("  No results found")
        
        print()
    
    # Interactive mode
    print("\n" + "="*60)
    print("INTERACTIVE SEARCH (type 'quit' to exit)")
    print("="*60 + "\n")
    
    while True:
        try:
            query = input("Search: ").strip()
            if not query or query.lower() == 'quit':
                break
            
            results = search.search(query, top_k=5)
            
            print("\nResults:")
            if results:
                for i, r in enumerate(results, 1):
                    m = r['metadata']
                    print(f"{i}. {m['name']} - ₹{m['price']} ({m['category']})")
                    print(f"   Score: {r['score']:.3f} | Similarity: {r['base_similarity']:.3f} | Boost: {r['boost_factor']:.2f}")
            else:
                print("No results found.")
            print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    search.close()
    print("\nSearch testing complete!")


if __name__ == "__main__":
    main()

    