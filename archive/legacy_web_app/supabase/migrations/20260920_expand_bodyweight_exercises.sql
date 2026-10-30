alter table jobs drop constraint if exists jobs_exercise_check;
alter table jobs add constraint jobs_exercise_check check (
  exercise in (
    'auto', 'squat', 'jumping_jack', 'push_up', 'pull_up', 'lunge',
    'sit_up', 'mountain_climber', 'burpee', 'plank'
  )
);
