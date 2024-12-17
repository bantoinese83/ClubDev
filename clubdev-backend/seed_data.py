import random
from faker import Faker
from sqlmodel import create_engine, Session

from app.db.models import (
    User,
    Role,
    AuthProvider,
    Achievement,
    Status,
    Badge,
    BadgeType,
    BlogPost,
    Comment,
    Challenge,
    DailyChallenge,
    Flag,
    Follow,
    GamificationEvent,
    GitHubRepo,
    HelpAnswer,
    HelpQuestion,
    Leaderboard,
    Like,
    Message,
    Notification,
    PageView,
    Payment,
    Script,
    ScriptView,
    SiteMetric,
    Subscription,
    SubscriptionPlan,
    Transaction,
    Trophy,
    TrophyLevel,
    UserAchievement,
    UserBadge,
    UserProfile,
    BlogPostView,
    PaymentStatus,
    SubscriptionStatus,
    DirectMessage
)

from app.core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, echo=True)
fake = Faker()

def seed_database():
    with Session(engine) as session:
        # Create Users
        users = []
        for _ in range(100):
            user = User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                hashed_password=fake.password(),
                auth_provider=random.choice(list(AuthProvider)),
                is_active=True,
                role=random.choice(list(Role)),
            )
            users.append(user)
        session.add_all(users)
        session.commit()
        for user in users:
            session.refresh(user)

        # Create User Profiles
        user_profiles = []
        for user in users:
            profile = UserProfile(
                user_id=user.id,
                bio=fake.text(max_nb_chars=200),
                location=fake.city(),
                avatar_url=fake.image_url(),
                website=fake.url(),
                github_username=fake.user_name(),
                twitter_username=fake.user_name()
            )
            user_profiles.append(profile)
        session.add_all(user_profiles)
        session.commit()
        for profile in user_profiles:
            session.refresh(profile)

        # Create Achievements
        achievements = [
            Achievement(name="First Script", description="Created your first script", status=Status.ACHIEVED),
            Achievement(name="Reviewer", description="Reviewed 10 scripts", status=Status.ACHIEVED),
            Achievement(name="Popular Creator", description="Your script has 50 likes", status=Status.LOCKED),
        ]
        session.add_all(achievements)
        session.commit()
        for achievement in achievements:
            session.refresh(achievement)

        # Create Badges
        badges = [
            Badge(name="Beginner", description="Just starting out", badge_type=BadgeType.ACHIEVEMENT),
            Badge(name="Upvoter", description="You like to vote", badge_type=BadgeType.PARTICIPATION),
            Badge(name="Pro", description="Code like a pro", badge_type=BadgeType.SPECIAL),
        ]
        session.add_all(badges)
        session.commit()
        for badge in badges:
            session.refresh(badge)

        # User Achievements
        user_achievements = []
        for user in users:
            user_achievement = UserAchievement(user_id=user.id, achievement_id=random.choice(achievements).id)
            user_achievements.append(user_achievement)
        session.add_all(user_achievements)
        session.commit()
        for user_achievement in user_achievements:
            session.refresh(user_achievement)

        # User Badges
        user_badges = []
        for user in users:
            user_badge = UserBadge(user_id=user.id, badge_id=random.choice(badges).id)
            user_badges.append(user_badge)
        session.add_all(user_badges)
        session.commit()
        for user_badge in user_badges:
            session.refresh(user_badge)

        # Create Scripts
        scripts = []
        for _ in range(100):
            script = Script(
                title=fake.unique.sentence(nb_words=3),
                content=fake.text(max_nb_chars=2000),
                language="Python",
                author_id=random.choice(users).id,
                description=fake.text(max_nb_chars=200),
                use_cases=fake.text(max_nb_chars=100),
                tags=fake.words(nb=5),
                grade=random.choice(["beginner", "intermediate", "advanced"]),
                framework=random.choice(["none", "Django", "Flask"]),
                license=random.choice(["MIT", "GPL", "Apache"]),
            )
            scripts.append(script)
        session.add_all(scripts)
        session.commit()
        for script in scripts:
            session.refresh(script)

        # Create Blog Posts
        blog_posts = []
        for _ in range(100):
            blog_post = BlogPost(
                title=fake.unique.sentence(nb_words=5),
                content=fake.text(max_nb_chars=2000),
                author_id=random.choice(users).id,
                tags=fake.words(nb=5),
                category=random.choice(["tech", "life", "coding", "tutorial"]),
            )
            blog_posts.append(blog_post)
        session.add_all(blog_posts)
        session.commit()
        for post in blog_posts:
            session.refresh(post)

        # Create Comments
        comments = []
        for _ in range(200):
            comment = Comment(
                user_id=random.choice(users).id,
                script_id=random.choice(scripts).id if random.choice([True, False]) else None,
                blog_post_id=random.choice(blog_posts).id if random.choice([True, False]) else None,
                content=fake.text(max_nb_chars=500),
            )
            comments.append(comment)
        session.add_all(comments)
        session.commit()
        for comment in comments:
            session.refresh(comment)

        # Create Likes
        likes = []
        for _ in range(200):
            like = Like(
                user_id=random.choice(users).id,
                script_id=random.choice(scripts).id if random.choice([True, False]) else None,
                blog_post_id=random.choice(blog_posts).id if random.choice([True, False]) else None,
            )
            likes.append(like)
        session.add_all(likes)
        session.commit()
        for like in likes:
            session.refresh(like)

        # Create Follows
        follows = []
        for _ in range(200):
            follow = Follow(
                follower_id=random.choice(users).id,
                followed_id=random.choice(users).id,
            )
            follows.append(follow)
        session.add_all(follows)
        session.commit()
        for follow in follows:
            session.refresh(follow)

        # Create Challenges
        challenges = [
            Challenge(
                name="Daily Upload",
                description="Upload a script today",
                type="daily",
                target=1,
                reward="50 XP",
            ),
            Challenge(
                name="Weekly Upvote",
                description="Upvote 10 scripts this week",
                type="weekly",
                target=10,
                reward="Upvoter Badge",
            )
        ]
        session.add_all(challenges)
        session.commit()
        for challenge in challenges:
            session.refresh(challenge)

        # Create Daily Challenges
        daily_challenges = []
        for user in users:
            daily_challenge = DailyChallenge(
                user_id=user.id,
                challenge_id=random.choice(challenges).id,
            )
            daily_challenges.append(daily_challenge)
        session.add_all(daily_challenges)
        session.commit()
        for daily_challenge in daily_challenges:
            session.refresh(daily_challenge)

        # Create Notifications
        notifications = []
        for user in users:
            notification = Notification(
                user_id=user.id,
                message=fake.sentence(nb_words=10),
            )
            notifications.append(notification)
        session.add_all(notifications)
        session.commit()
        for notification in notifications:
            session.refresh(notification)

        # Create Page Views
        page_views = []
        for user in users:
            page_view = PageView(
                user_id=user.id,
                page_url=fake.url(),
            )
            page_views.append(page_view)
        session.add_all(page_views)
        session.commit()
        for page_view in page_views:
            session.refresh(page_view)

        # Create Payments
        payments = []
        for user in users:
            payment = Payment(
                user_id=user.id,
                amount=random.uniform(10, 100),
                currency="USD",
                status=random.choice(list(PaymentStatus)),
                payment_reference=fake.uuid4(),
            )
            payments.append(payment)
        session.add_all(payments)
        session.commit()
        for payment in payments:
            session.refresh(payment)

        # Create Site Metrics
        site_metrics = [
            SiteMetric(metric_name="Total Users", value=len(users)),
            SiteMetric(metric_name="Scripts created", value=len(scripts)),
            SiteMetric(metric_name="Posts created", value=len(blog_posts)),
            SiteMetric(metric_name="Total likes", value=len(likes))
        ]
        session.add_all(site_metrics)
        session.commit()
        for metric in site_metrics:
            session.refresh(metric)

        # Create Subscription Plans
        subscription_plans = [
            SubscriptionPlan(name="Basic", price=10, currency="USD", features="Basic functionality", stripe_price_id="price_1"),
            SubscriptionPlan(name="Premium", price=20, currency="USD", features="All features included", stripe_price_id="price_2")
        ]
        session.add_all(subscription_plans)
        session.commit()
        for plan in subscription_plans:
            session.refresh(plan)

        # Create Subscriptions
        subscriptions = []
        for user in users:
            subscription = Subscription(
                user_id=user.id,
                plan_id=random.choice(subscription_plans).id,
                status=random.choice(list(SubscriptionStatus)),
            )
            subscriptions.append(subscription)
        session.add_all(subscriptions)
        session.commit()
        for subscription in subscriptions:
            session.refresh(subscription)

        # Create Transactions
        transactions = []
        for user in users:
            transaction = Transaction(
                user_id=user.id,
                amount=random.uniform(10, 200),
                transaction_type=random.choice(["subscription", "upgrade"]),
                stripe_transaction_id=fake.uuid4(),
            )
            transactions.append(transaction)
        session.add_all(transactions)
        session.commit()
        for transaction in transactions:
            session.refresh(transaction)

        # Create Trophies
        trophies = []
        for user in users:
            trophy = Trophy(
                name=fake.unique.sentence(nb_words=3),
                description=fake.text(max_nb_chars=200),
                trophy_level=random.choice(list(TrophyLevel)),
                status=random.choice(list(Status)),
                user_id=user.id,
            )
            trophies.append(trophy)
        session.add_all(trophies)
        session.commit()
        for trophy in trophies:
            session.refresh(trophy)

        # Create Gamification Events
        gamification_events = []
        for user in users:
            gamification_event = GamificationEvent(
                user_id=user.id,
                event_type=random.choice(["script_created", "post_created", "script_view"]),
                xp_reward=random.randint(10, 100),
            )
            gamification_events.append(gamification_event)
        session.add_all(gamification_events)
        session.commit()
        for gamification_event in gamification_events:
            session.refresh(gamification_event)

        # Create Help Questions
        help_questions = []
        for user in users:
            help_question = HelpQuestion(
                title=fake.unique.sentence(nb_words=5),
                content=fake.text(max_nb_chars=1000),
                asker_id=user.id,
            )
            help_questions.append(help_question)
        session.add_all(help_questions)
        session.commit()
        for question in help_questions:
            session.refresh(question)

        # Create Help Answers
        help_answers = []
        for question in help_questions:
            help_answer = HelpAnswer(
                question_id=question.id,
                responder_id=random.choice(users).id,
                content=fake.text(max_nb_chars=1000),
            )
            help_answers.append(help_answer)
        session.add_all(help_answers)
        session.commit()
        for help_answer in help_answers:
            session.refresh(help_answer)

        # Create GitHub Repos
        git_repos = []
        for user in users:
            git_repo = GitHubRepo(
                name=fake.unique.word(),
                url=fake.url(),
                owner_id=user.id,
            )
            git_repos.append(git_repo)
        session.add_all(git_repos)
        session.commit()
        for repo in git_repos:
            session.refresh(repo)

        # Create Leaderboards
        leaderboards = []
        for user in users:
            leaderboard = Leaderboard(
                user_id=user.id,
                ranking_criteria="xp",
                rank=random.randint(1, 100),
            )
            leaderboards.append(leaderboard)
        session.add_all(leaderboards)
        session.commit()
        for leaderboard in leaderboards:
            session.refresh(leaderboard)

        # Create Script Views
        script_views = []
        for user in users:
            script_view = ScriptView(
                script_id=random.choice(scripts).id,
                user_id=user.id,
            )
            script_views.append(script_view)
        session.add_all(script_views)
        session.commit()
        for view in script_views:
            session.refresh(view)

        # Create Blog Post Views
        blog_post_views = []
        for user in users:
            blog_post_view = BlogPostView(
                blog_post_id=random.choice(blog_posts).id,
                user_id=user.id,
            )
            blog_post_views.append(blog_post_view)
        session.add_all(blog_post_views)
        session.commit()
        for view in blog_post_views:
            session.refresh(view)

        # Create Flags
        flags = []
        for user in users:
            flag = Flag(
                reason=fake.sentence(nb_words=5),
                flagger_id=user.id,
                script_id=random.choice(scripts).id if random.choice([True, False]) else None,
                blog_post_id=random.choice(blog_posts).id if random.choice([True, False]) else None,
            )
            flags.append(flag)
        session.add_all(flags)
        session.commit()
        for flag in flags:
            session.refresh(flag)

        # Create Messages
        messages = []
        for _ in range(200):
            message = Message(
                sender_id=random.choice(users).id,
                receiver_id=random.choice(users).id,
                content=fake.text(max_nb_chars=1000),
            )
            messages.append(message)
        session.add_all(messages)
        session.commit()
        for message in messages:
            session.refresh(message)

        # Create Direct Messages
        direct_messages = []
        for _ in range(200):
            direct_message = DirectMessage(
                sender_id=random.choice(users).id,
                receiver_id=random.choice(users).id,
                content=fake.text(max_nb_chars=1000),
            )
            direct_messages.append(direct_message)
        session.add_all(direct_messages)
        session.commit()
        for direct_message in direct_messages:
            session.refresh(direct_message)

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()