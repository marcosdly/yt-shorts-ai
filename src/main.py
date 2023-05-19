import multiprocessing as mp
from video_cut_thread import watch_and_cut
from ai import config_openai
from ai_evaluation_thread import watch_db_and_evaluate_video_AI
from video_posting_thread import watch_db_and_post_video


def main() -> None:
    config_openai()
    processes = []
    video_cutting_process = mp.Process(target=watch_and_cut, name="Video_Cutting_Thread")
    ai_evaluation_process = mp.Process(target=watch_db_and_evaluate_video_AI,
                                      name="AI_Video_Content_Evaluation_Thread")
    video_posting_process = mp.Process(target=watch_db_and_post_video,
                                       name="Video_Posting_Thread")
    processes.append(video_cutting_process)
    processes.append(ai_evaluation_process)
    processes.append(video_posting_process)

    for p in processes: p.start()
    for p in processes: p.join()


if __name__ == "__main__":
    main()
