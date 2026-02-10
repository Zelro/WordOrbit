from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Max, Count, Avg
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Word, GameSession, UserProfile, Achievement, Feedback, WordHistory
from .forms import UserRegistrationForm, FeedbackForm, UserProfileForm
from .utils import generate_word_grid, get_random_words
import json
from datetime import datetime


def home(request):
    """Home page view with game statistics"""
    context = {
        'total_users': User.objects.count(),
        'total_games': GameSession.objects.count(),
        'total_words': Word.objects.count(),
        'top_players': UserProfile.objects.order_by('-highest_score')[:3],
    }
    return render(request, 'Wordapp/home.html', context)


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Welcome to WordOrbit, {username}! Your account has been created.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'Wordapp/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(
                request, f'Welcome back to WordOrbit, {username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(
                request, 'Invalid username or password. Please try again.')

    return render(request, 'Wordapp/login.html')


def user_logout(request):
    """User logout view"""
    username = request.user.username
    logout(request)
    messages.info(
        request, f'Goodbye {username}! You have been logged out successfully.')
    return redirect('home')


@login_required
def game_play(request):
    """Main game play view"""
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty', 'easy')
    else:
        difficulty = request.GET.get('difficulty', 'easy')

    grid_sizes = {'easy': 8, 'medium': 10, 'hard': 12}
    grid_size = grid_sizes.get(difficulty, 8)

    word_counts = {'easy': 5, 'medium': 7, 'hard': 10}
    word_count = word_counts.get(difficulty, 5)

    # IMPORTANT: Set max word length to grid size to ensure all words fit
    max_word_length = grid_size

    # Get words with length validation
    words = get_random_words(
        difficulty, count=word_count, max_length=max_word_length)

    if not words:
        messages.warning(
            request, 'Not enough words in the database. Please contact admin.')
        return redirect('home')

    word_list = [word.word.upper() for word in words]
    word_definitions = {word.word.upper(): word.definition for word in words}

    # Generate grid with validated words
    grid = generate_word_grid(word_list, grid_size)

    # Double-check: Only include words that were successfully placed
    # (This prevents the bug where words are in the list but not in the grid)
    placed_words = []
    for word in word_list:
        word_found = False
        # Quick check if word exists in grid
        grid_str = ''.join([''.join(row) for row in grid])
        if word in grid_str:
            word_found = True
        else:
            # Check all directions
            for row in range(grid_size):
                for col in range(grid_size):
                    # Check horizontal
                    if col + len(word) <= grid_size:
                        h_word = ''.join([grid[row][col + i]
                                         for i in range(len(word))])
                        if h_word == word:
                            word_found = True
                            break
                    # Check vertical
                    if row + len(word) <= grid_size:
                        v_word = ''.join([grid[row + i][col]
                                         for i in range(len(word))])
                        if v_word == word:
                            word_found = True
                            break
                    # Check diagonal down-right
                    if row + len(word) <= grid_size and col + len(word) <= grid_size:
                        d_word = ''.join([grid[row + i][col + i]
                                         for i in range(len(word))])
                        if d_word == word:
                            word_found = True
                            break
                    # Check diagonal down-left
                    if row + len(word) <= grid_size and col - len(word) >= -1:
                        dl_word = ''.join([grid[row + i][col - i]
                                          for i in range(len(word))])
                        if dl_word == word:
                            word_found = True
                            break
                if word_found:
                    break

        if word_found:
            placed_words.append(word)
        else:
            print(
                f"Warning: Word '{word}' was not placed in grid, removing from list")

    # Only use words that were actually placed
    final_word_list = placed_words
    final_definitions = {word: word_definitions[word] for word in placed_words}

    if len(final_word_list) < 3:
        messages.warning(
            request, 'Could not generate enough words for this game. Please try again.')
        return redirect('home')

    request.session['current_game'] = {
        'difficulty': difficulty,
        'grid_size': grid_size,
        'words': final_word_list,
        'definitions': final_definitions,
        'grid': grid,
        'start_time': datetime.now().isoformat(),
        'found_words': []
    }

    context = {
        'grid': grid,
        'words': final_word_list,
        'definitions': final_definitions,
        'difficulty': difficulty,
        'grid_size': grid_size,
        'word_count': len(final_word_list),
    }

    return render(request, 'Wordapp/game_play.html', context)


@login_required
def check_word(request):
    """AJAX view to check if found word is correct"""
    if request.method == 'POST':
        found_word = request.POST.get('word', '').upper()
        game_data = request.session.get('current_game', {})

        print(f"DEBUG check_word: received word = {found_word}")
        print(
            f"DEBUG check_word: game_data words = {game_data.get('words', [])}")
        print(
            f"DEBUG check_word: game_data found_words = {game_data.get('found_words', [])}")

        if found_word in game_data.get('words', []):
            if found_word not in game_data.get('found_words', []):
                # Add to found words list
                if 'found_words' not in game_data:
                    game_data['found_words'] = []
                game_data['found_words'].append(found_word)

                # CRITICAL: Save back to session
                request.session['current_game'] = game_data
                request.session.modified = True

                print(
                    f"DEBUG check_word: Updated found_words = {game_data['found_words']}")

                return JsonResponse({
                    'status': 'success',
                    'message': f'Excellent! You found "{found_word}"!',
                    'definition': game_data.get('definitions', {}).get(found_word, ''),
                    'found_words': game_data['found_words'],
                    'total_found': len(game_data['found_words'])
                })
            else:
                return JsonResponse({
                    'status': 'duplicate',
                    'message': 'You already found this word!'
                })

        return JsonResponse({
            'status': 'error',
            'message': 'Word not found in the list. Keep searching!'
        })


@login_required
def end_game(request):
    """End game and calculate score"""
    if request.method == 'POST':
        game_data = request.session.get('current_game', {})

        if not game_data:
            messages.warning(request, 'No active game found.')
            return redirect('game_play')

        start_time = datetime.fromisoformat(game_data['start_time'])
        time_taken = int((datetime.now() - start_time).total_seconds())

        # Format time as MM:SS
        minutes = time_taken // 60
        seconds = time_taken % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        # CRITICAL FIX: Ensure we get found_words correctly
        found_words_list = game_data.get('found_words', [])
        words_found = len(found_words_list)
        total_words = len(game_data.get('words', []))

        # Debug logging
        print(f"DEBUG: found_words_list = {found_words_list}")
        print(f"DEBUG: words_found = {words_found}")
        print(f"DEBUG: total_words = {total_words}")

        # Don't allow ending with 0 words
        if words_found == 0:
            messages.warning(
                request, 'You must find at least one word before ending the game!')
            return redirect('game_play')

        base_score = words_found * 100

        difficulty_multipliers = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
        difficulty = game_data.get('difficulty', 'easy')
        difficulty_bonus = int(
            base_score * difficulty_multipliers.get(difficulty, 1.0) - base_score)

        time_bonus = max(0, (300 - time_taken)
                         ) // 10 if time_taken < 300 else 0
        completion_bonus = 200 if words_found == total_words else 0

        score = base_score + difficulty_bonus + time_bonus + completion_bonus

        # Save game session
        game_session = GameSession.objects.create(
            user=request.user,
            difficulty=difficulty,
            grid_size=game_data['grid_size'],
            words_found=words_found,
            total_words=total_words,
            score=score,
            time_taken=time_taken,
            completed=(words_found == total_words)
        )

        # Update user profile - CRITICAL FIX
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.total_games += 1
        profile.total_score += score
        profile.words_discovered += words_found  # This should work now
        if score > profile.highest_score:
            profile.highest_score = score
        profile.save()

        print(
            f"DEBUG: Profile updated - words_discovered now: {profile.words_discovered}")

        # Check achievements
        check_achievements(request.user, profile, words_found,
                           score, time_taken, total_words)

        # Store results in session
        request.session['last_game_results'] = {
            'score': score,
            'words_found': words_found,
            'total_words': total_words,
            'time_taken': time_taken,
            'formatted_time': formatted_time,
            'difficulty': difficulty,
            'base_score': base_score,
            'difficulty_bonus': difficulty_bonus,
            'time_bonus': time_bonus,
            'completion_bonus': completion_bonus,
        }

        # Clear current game
        request.session.pop('current_game', None)
        request.session.modified = True

        messages.success(
            request, f'Game completed! Your score: {score} points!')
        return redirect('game_results')

    return redirect('game_play')
    """End game and calculate score"""
    if request.method == 'POST':
        game_data = request.session.get('current_game', {})

        if not game_data:
            messages.warning(request, 'No active game found.')
            return redirect('game_play')

        start_time = datetime.fromisoformat(game_data['start_time'])
        time_taken = int((datetime.now() - start_time).total_seconds())

        # Format time as MM:SS
        minutes = time_taken // 60
        seconds = time_taken % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        words_found = len(game_data.get('found_words', []))
        total_words = len(game_data.get('words', []))

        # IMPORTANT FIX: Don't allow game completion with 0 words found
        if words_found == 0:
            messages.warning(
                request, 'You must find at least one word before ending the game!')
            # Don't clear session - let them continue playing
            return redirect('game_play')

        base_score = words_found * 100

        difficulty_multipliers = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
        difficulty = game_data.get('difficulty', 'easy')
        difficulty_bonus = int(
            base_score * difficulty_multipliers.get(difficulty, 1.0) - base_score)

        time_bonus = max(0, (300 - time_taken)
                         ) // 10 if time_taken < 300 else 0
        completion_bonus = 200 if words_found == total_words else 0

        score = base_score + difficulty_bonus + time_bonus + completion_bonus

        # Save game session to database
        game_session = GameSession.objects.create(
            user=request.user,
            difficulty=difficulty,
            grid_size=game_data['grid_size'],
            words_found=words_found,
            total_words=total_words,
            score=score,
            time_taken=time_taken,
            completed=(words_found == total_words)
        )

        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.total_games += 1
        profile.total_score += score
        profile.words_discovered += words_found
        if score > profile.highest_score:
            profile.highest_score = score
        profile.save()

        # Check for achievements
        check_achievements(request.user, profile, words_found,
                           score, time_taken, total_words)

        # Store results in session for display
        request.session['last_game_results'] = {
            'score': score,
            'words_found': words_found,
            'total_words': total_words,
            'time_taken': time_taken,
            'formatted_time': formatted_time,
            'difficulty': difficulty,
            'base_score': base_score,
            'difficulty_bonus': difficulty_bonus,
            'time_bonus': time_bonus,
            'completion_bonus': completion_bonus,
        }

        # IMPORTANT: Clear current game session AFTER saving everything
        request.session.pop('current_game', None)
        request.session.modified = True

        messages.success(
            request, f'Game completed! Your score: {score} points!')
        return redirect('game_results')

    return redirect('game_play')
    """End game and calculate score"""
    if request.method == 'POST':
        game_data = request.session.get('current_game', {})

        if not game_data:
            messages.warning(request, 'No active game found.')
            return redirect('game_play')

        start_time = datetime.fromisoformat(game_data['start_time'])
        time_taken = int((datetime.now() - start_time).total_seconds())

        # Format time as MM:SS
        minutes = time_taken // 60
        seconds = time_taken % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        words_found = len(game_data.get('found_words', []))
        total_words = len(game_data.get('words', []))

        # IMPORTANT FIX: Don't allow game completion with 0 words found
        if words_found == 0:
            messages.warning(
                request, 'You must find at least one word before ending the game!')
            return redirect('game_play')

        base_score = words_found * 100

        difficulty_multipliers = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
        difficulty = game_data.get('difficulty', 'easy')
        difficulty_bonus = int(
            base_score * difficulty_multipliers.get(difficulty, 1.0) - base_score)

        time_bonus = max(0, (300 - time_taken)
                         ) // 10 if time_taken < 300 else 0
        completion_bonus = 200 if words_found == total_words else 0

        score = base_score + difficulty_bonus + time_bonus + completion_bonus

        game_session = GameSession.objects.create(
            user=request.user,
            difficulty=difficulty,
            grid_size=game_data['grid_size'],
            words_found=words_found,
            total_words=total_words,
            score=score,
            time_taken=time_taken,
            completed=(words_found == total_words)
        )

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.total_games += 1
        profile.total_score += score
        profile.words_discovered += words_found
        if score > profile.highest_score:
            profile.highest_score = score
        profile.save()

        check_achievements(request.user, profile, words_found,
                           score, time_taken, total_words)

        request.session['last_game_results'] = {
            'score': score,
            'words_found': words_found,
            'total_words': total_words,
            'time_taken': time_taken,
            'formatted_time': formatted_time,
            'difficulty': difficulty,
            'base_score': base_score,
            'difficulty_bonus': difficulty_bonus,
            'time_bonus': time_bonus,
            'completion_bonus': completion_bonus,
        }

        request.session.pop('current_game', None)

        messages.success(
            request, f'Game completed! Your score: {score} points!')
        return redirect('game_results')

    return redirect('game_play')
    """End game and calculate score"""
    if request.method == 'POST':
        game_data = request.session.get('current_game', {})

        if not game_data:
            messages.warning(request, 'No active game found.')
            return redirect('game_play')

        start_time = datetime.fromisoformat(game_data['start_time'])
        time_taken = int((datetime.now() - start_time).total_seconds())

        # Format time as MM:SS
        minutes = time_taken // 60
        seconds = time_taken % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        words_found = len(game_data.get('found_words', []))
        total_words = len(game_data.get('words', []))

        base_score = words_found * 100

        difficulty_multipliers = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
        difficulty = game_data.get('difficulty', 'easy')
        difficulty_bonus = int(
            base_score * difficulty_multipliers.get(difficulty, 1.0) - base_score)

        time_bonus = max(0, (300 - time_taken)
                         ) // 10 if time_taken < 300 else 0
        completion_bonus = 200 if words_found == total_words else 0

        score = base_score + difficulty_bonus + time_bonus + completion_bonus

        game_session = GameSession.objects.create(
            user=request.user,
            difficulty=difficulty,
            grid_size=game_data['grid_size'],
            words_found=words_found,
            total_words=total_words,
            score=score,
            time_taken=time_taken,
            completed=(words_found == total_words)
        )

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.total_games += 1
        profile.total_score += score
        profile.words_discovered += words_found
        if score > profile.highest_score:
            profile.highest_score = score
        profile.save()

        check_achievements(request.user, profile, words_found,
                           score, time_taken, total_words)

        request.session['last_game_results'] = {
            'score': score,
            'words_found': words_found,
            'total_words': total_words,
            'time_taken': time_taken,
            'formatted_time': formatted_time,  # ADDED THIS LINE
            'difficulty': difficulty,
            'base_score': base_score,
            'difficulty_bonus': difficulty_bonus,
            'time_bonus': time_bonus,
            'completion_bonus': completion_bonus,
        }

        request.session.pop('current_game', None)

        messages.success(
            request, f'Game completed! Your score: {score} points!')
        return redirect('game_results')

    return redirect('game_play')


def check_achievements(user, profile, words_found, score, time_taken, total_words):
    """Check and award achievements"""
    achievements = []

    if profile.total_games == 1:
        achievements.append({
            'name': 'First Steps',
            'description': 'Completed your first WordOrbit game!',
            'type': 'first_game'
        })

    if words_found == total_words:
        achievements.append({
            'name': 'Word Master',
            'description': 'Found all words in a game!',
            'type': 'word_master'
        })

    if score >= 500:
        achievements.append({
            'name': 'High Scorer',
            'description': 'Scored 500+ points in a single game!',
            'type': 'high_scorer'
        })

    if time_taken < 120 and words_found == total_words:
        achievements.append({
            'name': 'Speed Demon',
            'description': 'Completed a game in under 2 minutes!',
            'type': 'speed_demon'
        })

    if profile.total_games >= 10:
        achievements.append({
            'name': 'Dedicated Player',
            'description': 'Played 10 games!',
            'type': 'dedicated_player'
        })

    if profile.words_discovered >= 100:
        achievements.append({
            'name': 'Century Club',
            'description': 'Discovered 100 words!',
            'type': 'streak_master'
        })

    for ach in achievements:
        Achievement.objects.get_or_create(
            user=user,
            name=ach['name'],
            defaults={
                'description': ach['description'],
                'achievement_type': ach['type']
            }
        )


@login_required
def game_results(request):
    """Display game results"""
    results = request.session.get('last_game_results')

    if not results:
        messages.warning(
            request, 'No game results found. Please play a game first.')
        return redirect('game_play')

    return render(request, 'Wordapp/game_results.html', {'results': results})
    """Display game results"""
    results = request.session.get('last_game_results')

    if not results:
        messages.warning(
            request, 'No game results found. Please play a game first.')
        return redirect('game_play')

    # request.session.pop('last_game_results', None)

    return render(request, 'Wordapp/game_results.html', {'results': results})


@login_required
def profile(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    recent_games = GameSession.objects.filter(user=request.user)[:10]
    achievements = Achievement.objects.filter(user=request.user)

    total_time = GameSession.objects.filter(user=request.user).aggregate(
        Sum('time_taken'))['time_taken__sum'] or 0

    context = {
        'profile': profile,
        'recent_games': recent_games,
        'achievements': achievements,
        'total_time_played': total_time,
    }

    return render(request, 'Wordapp/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'Wordapp/edit_profile.html', {'form': form})


def leaderboard(request):
    """Leaderboard view"""
    top_players = UserProfile.objects.order_by('-highest_score')[:20]

    # Get difficulty filter FIRST, before slicing
    difficulty = request.GET.get('difficulty', 'all')

    # Start with base queryset
    recent_games = GameSession.objects.all().order_by('-score')

    # Apply filter BEFORE slicing
    if difficulty != 'all':
        recent_games = recent_games.filter(difficulty=difficulty)

    # Now slice to get top 20
    recent_games = recent_games[:20]

    context = {
        'top_players': top_players,
        'recent_games': recent_games,
        'selected_difficulty': difficulty,
    }

    return render(request, 'Wordapp/leaderboard.html', context)


def contact(request):
    """Contact page view"""
    context = {
        'email': 'denzelkoro@gmail.com',
        'phone': '+234-90-130-85531',
        'address': 'Lagos, Nigeria'
    }
    return render(request, 'Wordapp/contact.html', context)


def feedback(request):
    """Feedback form view"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_obj = form.save(commit=False)
            if request.user.is_authenticated:
                feedback_obj.user = request.user
            feedback_obj.save()
            messages.success(
                request, 'Thank you for your feedback! We appreciate your input.')
            return redirect('home')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email
            }
        form = FeedbackForm(initial=initial_data)

    return render(request, 'Wordapp/feedback.html', {'form': form})


def about(request):
    """About page"""
    return render(request, 'Wordapp/about.html')
