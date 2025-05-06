<template>
  <div id="login">
    <h1>登录</h1>
    <form @submit.prevent="loginUser">
      <div class="form-group">
        <label for="username">用户名：</label>
        <input type="text" v-model="username" id="username" class="form-control" required/>
      </div>
      <div class="form-group">
        <label for="password">密码：</label>
        <input type="password" v-model="password" id="password" class="form-control" required/>
      </div>
      <div class="form-group d-flex justify-content-between">
        <button type="submit" class="btn btn-primary">登录</button>
        <p class="m-0 align-self-center">没有账号？
          <router-link to="/register">注册</router-link>
        </p>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  created() {
    // 检查 localStorage 中是否已经有登录信息
    const userId = localStorage.getItem('userId');
    const userRole = localStorage.getItem('userRole');

    if (userId && userRole) {
      // 如果有登录信息，根据角色跳转到相应页面
      if (userRole === '1') {
        // 如果是管理员，跳转到 all-studyrooms 页面
        this.$router.push({name: 'all_studyrooms', params: {userId}});
      } else {
        // 如果是普通用户，跳转到 ibooking-index 页面
        this.$router.push({name: 'ibooking_index', params: {userId}});
      }
    }
  },
  methods: {
    loginUser() {
      // 登录请求，确保数据格式与 FastAPI 后端要求的一致
      this.$http
          .post('http://127.0.0.1:8090/user/login', {username: this.username, password: this.password})
          .then(
              (response) => {
                if (response.body.status === 200) {
                  const userData = response.body.data;
                  const userId = userData.id; // 假设 id 在返回的数据中
                  const userRole = userData.role; // 假设 role 在返回的数据中
                  const userName = userData.username;

                  // 将用户信息存储到 localStorage
                  localStorage.setItem('userId', userId);
                  localStorage.setItem('userRole', userRole); // 存储角色信息，普通用户为 0，管理员为 1
                  localStorage.setItem('userName', userName);

                  // 根据角色跳转到不同的页面
                  if (userRole === 1) {
                    // 如果是管理员，跳转到 all-studyrooms 页面
                    this.$router.push({name: 'all_studyrooms', params: {userId}});
                  } else {
                    // 如果是普通用户，跳转到 ibooking-index 页面
                    this.$router.push({name: 'ibooking_index', params: {userId}});
                  }
                } else {
                  alert(response.body.message || '用户名或密码错误');
                }
              },
              (error) => {
                if (error.body && error.body.detail) {
                  alert(error.body.detail || '用户名或密码错误');
                } else {
                  alert('登录失败，服务器异常');
                }
              }
          );
    }
  }
};
</script>

<style scoped>
#login {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

h1 {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 10px;
}

/* 登录按钮和链接水平对齐 */
.d-flex {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

button {
  margin-top: 10px;
}

p {
  margin-bottom: 0; /* 防止多余的底部间距 */
}

router-link {
  text-decoration: none;
  color: #007bff;
}
</style>
