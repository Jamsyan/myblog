/**
 * 错误处理工具
 * 统一处理应用中的错误
 */

/**
 * 错误类型枚举
 */
export const ErrorType = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  API_ERROR: 'API_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  PERMISSION_ERROR: 'PERMISSION_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

/**
 * 错误消息映射
 */
const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败,请检查网络设置',
  API_ERROR: '服务器错误,请稍后重试',
  AUTH_ERROR: '认证失败,请重新登录',
  VALIDATION_ERROR: '输入数据有误,请检查后重试',
  PERMISSION_ERROR: '权限不足,无法执行此操作',
  UNKNOWN_ERROR: '发生未知错误,请稍后重试',
  TIMEOUT_ERROR: '请求超时,请稍后重试',
  INVALID_CREDENTIALS: '用户名或密码错误',
  USER_EXISTS: '用户名或邮箱已存在',
  USER_NOT_FOUND: '用户不存在',
  POST_NOT_FOUND: '文章不存在',
  MISSING_REQUIRED_FIELD: '缺少必填字段'
};

/**
 * 应用错误类
 */
export class AppError extends Error {
  constructor(message, type = ErrorType.UNKNOWN_ERROR, code = null, details = null) {
    super(message);
    this.name = 'AppError';
    this.type = type;
    this.code = code;
    this.details = details;
  }
}

/**
 * 解析错误消息
 * @param {string|Error} error - 错误对象或错误消息
 * @returns {Object} 解析后的错误信息
 */
export const parseError = (error) => {
  if (error instanceof AppError) {
    return {
      message: error.message,
      type: error.type,
      code: error.code,
      details: error.details
    };
  }

  if (error instanceof Error) {
    const message = error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
    
    let type = ErrorType.UNKNOWN_ERROR;
    if (message.includes('Failed to fetch') || message.includes('网络')) {
      type = ErrorType.NETWORK_ERROR;
    } else if (message.includes('401') || message.includes('认证') || message.includes('登录')) {
      type = ErrorType.AUTH_ERROR;
    } else if (message.includes('403') || message.includes('权限')) {
      type = ErrorType.PERMISSION_ERROR;
    } else if (message.includes('400') || message.includes('验证') || message.includes('必填')) {
      type = ErrorType.VALIDATION_ERROR;
    } else if (message.includes('500') || message.includes('服务器')) {
      type = ErrorType.API_ERROR;
    }

    return {
      message,
      type,
      code: null,
      details: null
    };
  }

  return {
    message: error || ERROR_MESSAGES.UNKNOWN_ERROR,
    type: ErrorType.UNKNOWN_ERROR,
    code: null,
    details: null
  };
};

/**
 * 获取友好的错误消息
 * @param {string|Error} error - 错误对象或错误消息
 * @returns {string} 友好的错误消息
 */
export const getErrorMessage = (error) => {
  const parsed = parseError(error);
  
  if (parsed.message.includes('Invalid username or password')) {
    return ERROR_MESSAGES.INVALID_CREDENTIALS;
  }
  if (parsed.message.includes('username or email may already exist')) {
    return ERROR_MESSAGES.USER_EXISTS;
  }
  if (parsed.message.includes('User not found')) {
    return ERROR_MESSAGES.USER_NOT_FOUND;
  }
  if (parsed.message.includes('Post not found')) {
    return ERROR_MESSAGES.POST_NOT_FOUND;
  }
  if (parsed.message.includes('Missing required field')) {
    return ERROR_MESSAGES.MISSING_REQUIRED_FIELD;
  }
  if (parsed.message.includes('超时')) {
    return ERROR_MESSAGES.TIMEOUT_ERROR;
  }

  return ERROR_MESSAGES[parsed.type] || parsed.message;
};

/**
 * 创建应用错误
 * @param {string} message - 错误消息
 * @param {string} type - 错误类型
 * @param {string} code - 错误代码
 * @param {Object} details - 错误详情
 * @returns {AppError} 应用错误对象
 */
export const createError = (message, type = ErrorType.UNKNOWN_ERROR, code = null, details = null) => {
  return new AppError(message, type, code, details);
};

/**
 * 处理 API 错误
 * @param {Error} error - 错误对象
 * @returns {AppError} 应用错误对象
 */
export const handleApiError = (error) => {
  const parsed = parseError(error);
  const message = getErrorMessage(error);
  
  return new AppError(message, parsed.type, parsed.code, parsed.details);
};

/**
 * 错误处理器类
 */
export class ErrorHandler {
  constructor() {
    this.handlers = [];
  }

  /**
   * 注册错误处理器
   * @param {Function} handler - 错误处理函数
   */
  register(handler) {
    this.handlers.push(handler);
  }

  /**
   * 处理错误
   * @param {Error} error - 错误对象
   */
  handle(error) {
    const parsed = parseError(error);
    const message = getErrorMessage(error);
    
    this.handlers.forEach(handler => {
      try {
        handler(parsed, message);
      } catch (e) {
        console.error('错误处理器执行失败:', e);
      }
    });

    console.error('错误:', parsed);
  }
}

/**
 * 导出全局错误处理器实例
 */
export const errorHandler = new ErrorHandler();

/**
 * 默认错误处理:在控制台显示错误
 */
errorHandler.register((error, message) => {
  console.error(`[${error.type}] ${message}`);
});

export default {
  ErrorType,
  AppError,
  parseError,
  getErrorMessage,
  createError,
  handleApiError,
  ErrorHandler,
  errorHandler
};