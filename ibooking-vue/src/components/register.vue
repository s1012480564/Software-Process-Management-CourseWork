<template>
  <div id="register">
    <h1>注册</h1>
    <form @submit.prevent="registerUser">
      <div class="form-group">
        <label for="username">用户名：</label>
        <input type="text" v-model="username" id="username" class="form-control" required/>
      </div>
      <div class="form-group">
        <label for="stu_no">学号：</label>
        <input type="text" v-model="stu_no" id="stu_no" class="form-control" required/>
      </div>
      <div class="form-group">
        <label for="password">密码：</label>
        <input type="password" v-model="password" id="password" class="form-control" required/>
      </div>
      <div class="form-group">
        <label for="confirmPassword">确认密码：</label>
        <input type="password" v-model="confirmPassword" id="confirmPassword" class="form-control" required/>
      </div>
      <div class="form-group d-flex justify-content-between">
        <button type="submit" class="btn btn-primary">注册</button>
        <p class="m-0 align-self-center">已有账号？
          <router-link to="/login">登录</router-link>
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
      stu_no: '',
      password: '',
      confirmPassword: ''
    };
  },
  methods: {
    registerUser() {
      if (this.password !== this.confirmPassword) {
        alert('两次输入密码不一致');
        return;
      }

      // 假设调用后端API进行注册
      this.$http
          .post('http://127.0.0.1:8090/user/register', {
            username: this.username,
            stu_no: this.stu_no,
            password: this.password
          })
          .then(
              (response) => {
                if (response.body.status === 200) {
                  // 注册成功后跳转到登录页面
                  alert('注册成功，正在跳转到登录页面');
                  this.$router.push({name: 'login'});
                } else {
                  alert(response.body.message || '用户名或学号已被使用');
                }
              },
              (error) => {
                if (error.body && error.body.detail) {
                  alert(error.body.detail || '用户名或学号已被使用');
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
#register {
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