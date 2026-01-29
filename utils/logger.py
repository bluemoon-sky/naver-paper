"""
로깅 시스템 설정 모듈

기능:
- 콘솔 및 파일 로깅 지원
- 로그 레벨별 필터링 (DEBUG, INFO, WARNING, ERROR)
- UTF-8 인코딩 지원 (한글 로그)
- 타임스탬프 자동 추가 (KST 강제)
- 오래된 로그 자동 삭제 (3일)
"""
import logging
import os
import glob
from datetime import datetime, timedelta
import pytz


class KSTFormatter(logging.Formatter):
    """한국 시간(KST)을 강제하는 포매터"""
    def converter(self, timestamp):
        # UTC 타임스탬프를 KST로 올바르게 변환
        dt_utc = datetime.utcfromtimestamp(timestamp)
        return pytz.utc.localize(dt_utc).astimezone(pytz.timezone('Asia/Seoul'))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


def cleanup_old_logs(log_dir, days=3):
    """
    지정된 기간(일)보다 오래된 로그 파일을 삭제합니다.
    파일명 형식: prefix_YYYY-MM-DD.log
    """
    if not os.path.exists(log_dir):
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    
    # logs 폴더 내의 모든 .log 파일 검색
    for log_file in glob.glob(os.path.join(log_dir, "*.log")):
        try:
            # 파일명에서 날짜 추출 (예: naverpaper_2026-01-26.log)
            filename = os.path.basename(log_file)
            date_str = filename.replace('.log', '').split('_')[-1]
            
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            if file_date < cutoff_date:
                os.remove(log_file)
        except (ValueError, IndexError):
            continue
        except Exception:
            continue


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    로거를 설정하고 반환합니다.

    Args:
        name (str): 로거 이름 (보통 모듈명 __name__ 사용)
        log_file (str, optional): 로그 파일 경로. None이면 파일 저장 안 함.
        level (int, optional): 로그 레벨. 기본값은 INFO.

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 기존 핸들러 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()

    # KST 포매터 사용
    formatter = KSTFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (선택)
    if log_file:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # [추가] 오래된 로그 삭제 실행 (3일)
        cleanup_old_logs(log_dir, days=3)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_log_filename(prefix='naverpaper'):
    """
    날짜 기반 로그 파일명을 생성합니다. (KST 기준)

    Args:
        prefix (str): 로그 파일명 접두사

    Returns:
        str: 로그 파일 경로 (예: logs/naverpaper_2025-01-03.log)
    """
    kst_now = datetime.now(pytz.timezone('Asia/Seoul'))
    today = kst_now.strftime('%Y-%m-%d')
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f'{prefix}_{today}.log')
