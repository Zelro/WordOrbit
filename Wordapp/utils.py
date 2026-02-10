import random
from .models import Word


def get_random_words(difficulty, count=5, max_length=None):
    """
    Get random words based on difficulty level
    Filters out words that are too long for the grid
    """
    words = Word.objects.filter(difficulty=difficulty)

    # Get all words first, then filter by length in Python
    words_list = list(words)

    # Filter by max length if specified
    if max_length:
        words_list = [word for word in words_list if len(
            word.word) <= max_length]

    if len(words_list) < count:
        # Try all difficulties if not enough words
        words_list = list(Word.objects.all())
        if max_length:
            words_list = [word for word in words_list if len(
                word.word) <= max_length]

    if len(words_list) < count:
        return words_list

    return random.sample(words_list, min(count, len(words_list)))


def generate_word_grid(words, size):
    """
    Generate a grid with hidden words
    Words can be placed horizontally, vertically, or diagonally
    ENCOURAGES letter reuse by prioritizing intersecting placements
    Only includes words that can actually be placed
    """
    # Filter out words that are too long for the grid
    valid_words = [word for word in words if len(word) <= size]

    if len(valid_words) < len(words):
        print(
            f"Warning: Filtered out {len(words) - len(valid_words)} words that were too long for {size}x{size} grid")

    grid = [['' for _ in range(size)] for _ in range(size)]
    placed_words = []
    failed_words = []

    # Directions
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal down-right
        (1, -1),  # Diagonal down-left
    ]

    # Sort words by length (longer first)
    sorted_words = sorted(valid_words, key=len, reverse=True)

    for word_index, word in enumerate(sorted_words):
        placed = False
        attempts = 0
        max_attempts = 300  # Increased from 200

        best_placement = None
        best_intersections = 0

        while attempts < max_attempts:
            direction = random.choice(directions)
            row_step, col_step = direction

            # Calculate valid starting positions
            if row_step == 0:  # Horizontal
                if size - len(word) < 0:
                    attempts += 1
                    continue
                start_row = random.randint(0, size - 1)
                start_col = random.randint(0, size - len(word))
            elif col_step == 0:  # Vertical
                if size - len(word) < 0:
                    attempts += 1
                    continue
                start_row = random.randint(0, size - len(word))
                start_col = random.randint(0, size - 1)
            elif col_step == 1:  # Diagonal down-right
                if size - len(word) < 0:
                    attempts += 1
                    continue
                start_row = random.randint(0, size - len(word))
                start_col = random.randint(0, size - len(word))
            else:  # Diagonal down-left
                if size - len(word) < 0:
                    attempts += 1
                    continue
                start_row = random.randint(0, size - len(word))
                start_col = random.randint(len(word) - 1, size - 1)

            # Check if word can be placed
            can_place, intersections = can_place_word_with_intersections(
                grid, word, start_row, start_col, row_step, col_step
            )

            if can_place:
                # For first word or if no intersections yet, place immediately
                if word_index == 0 or attempts > 200:
                    place_word(grid, word, start_row,
                               start_col, row_step, col_step)
                    placed_words.append({
                        'word': word,
                        'start': (start_row, start_col),
                        'direction': (row_step, col_step)
                    })
                    placed = True
                    break

                # For other words, try to find placement with most intersections
                if intersections > best_intersections:
                    best_intersections = intersections
                    best_placement = (start_row, start_col, row_step, col_step)

                # If we found a good intersection, use it
                if intersections >= 2 or (intersections >= 1 and attempts > 50):
                    place_word(grid, word, start_row,
                               start_col, row_step, col_step)
                    placed_words.append({
                        'word': word,
                        'start': (start_row, start_col),
                        'direction': (row_step, col_step)
                    })
                    placed = True
                    break

            attempts += 1

        # If no intersection found but we have a valid placement, use it
        if not placed and best_placement:
            start_row, start_col, row_step, col_step = best_placement
            place_word(grid, word, start_row, start_col, row_step, col_step)
            placed_words.append({
                'word': word,
                'start': (start_row, start_col),
                'direction': (row_step, col_step)
            })
            placed = True

        if not placed:
            print(f"Warning: Could not place word '{word}' in grid")
            failed_words.append(word)

    # Fill empty cells with random letters
    for i in range(size):
        for j in range(size):
            if grid[i][j] == '':
                grid[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    # Log placement results
    if failed_words:
        print(f"Failed to place {len(failed_words)} words: {failed_words}")
    print(
        f"Successfully placed {len(placed_words)} out of {len(sorted_words)} words")

    return grid


def can_place_word_with_intersections(grid, word, row, col, row_step, col_step):
    """
    Check if word can be placed and count how many letters it shares
    Returns: (can_place: bool, intersection_count: int)
    """
    size = len(grid)
    intersections = 0

    for i, char in enumerate(word):
        r = row + i * row_step
        c = col + i * col_step

        # Check bounds
        if r < 0 or r >= size or c < 0 or c >= size:
            return False, 0

        # If cell is occupied
        if grid[r][c] != '':
            # If same letter, it's an intersection (good!)
            if grid[r][c] == char:
                intersections += 1
            else:
                # Different letter, can't place here
                return False, 0

    return True, intersections


def place_word(grid, word, row, col, row_step, col_step):
    """Place a word in the grid"""
    for i, char in enumerate(word):
        r = row + i * row_step
        c = col + i * col_step
        grid[r][c] = char


def can_place_word(grid, word, row, col, row_step, col_step):
    """Legacy function for compatibility"""
    can_place, _ = can_place_word_with_intersections(
        grid, word, row, col, row_step, col_step)
    return can_place


def calculate_score(words_found, total_words, time_taken, difficulty):
    """Calculate game score"""
    base_score = words_found * 100

    difficulty_multipliers = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
    difficulty_bonus = int(
        base_score * difficulty_multipliers.get(difficulty, 1.0) - base_score)

    if time_taken < 60:
        time_bonus = 300
    elif time_taken < 120:
        time_bonus = 200
    elif time_taken < 180:
        time_bonus = 100
    elif time_taken < 300:
        time_bonus = 50
    else:
        time_bonus = 0

    completion_bonus = 200 if words_found == total_words else 0
    total_score = base_score + difficulty_bonus + time_bonus + completion_bonus

    return {
        'base_score': base_score,
        'difficulty_bonus': difficulty_bonus,
        'time_bonus': time_bonus,
        'completion_bonus': completion_bonus,
        'total_score': total_score
    }


def get_achievement_progress(user_profile):
    """Calculate achievement progress"""
    progress = {
        'games_milestone': {
            'current': user_profile.total_games,
            'target': 10,
            'percentage': min(100, (user_profile.total_games / 10) * 100)
        },
        'words_milestone': {
            'current': user_profile.words_discovered,
            'target': 100,
            'percentage': min(100, (user_profile.words_discovered / 100) * 100)
        },
        'score_milestone': {
            'current': user_profile.highest_score,
            'target': 1000,
            'percentage': min(100, (user_profile.highest_score / 1000) * 100)
        }
    }
    return progress


def format_time(seconds):
    """Format time in seconds to MM:SS format"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def get_difficulty_stats(user):
    """Get user statistics by difficulty level"""
    from django.db.models import Count, Avg, Sum
    from .models import GameSession

    stats = {}
    for difficulty in ['easy', 'medium', 'hard']:
        games = GameSession.objects.filter(user=user, difficulty=difficulty)
        stats[difficulty] = {
            'games_played': games.count(),
            'avg_score': games.aggregate(Avg('score'))['score__avg'] or 0,
            'total_words_found': games.aggregate(Sum('words_found'))['words_found__sum'] or 0,
            'completion_rate': games.filter(completed=True).count() / games.count() * 100 if games.count() > 0 else 0
        }
    return stats
