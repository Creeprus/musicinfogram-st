import Icons from "../components/icons"

export default [
  {
    title: 'Альбомы',
    href: '/recipes',
    auth: false
  }, {
    title: 'Создать альбом',
    href: '/recipes/create',
    auth: true
  }, {
    title: 'О проекте',
    href: '/about',
    auth: false
  }
]

export const UserMenu = [
  {
    title: 'Мои подписки',
    href: '/subscriptions',
    auth: true,
    icon: <Icons.SubscriptionsMenu />
  }, {
    title: 'Избранное',
    href: '/favorites',
    auth: true,
    icon: <Icons.SavedMenu />
  }, {
    
    title: 'Сменить пароль',
    href: '/change-password',
    auth: true,
    icon: <Icons.ResetPasswordMenu />
  }
]

export const NotLoggedInMenu = [
  {
    title: 'Войти',
    href: '/signin',
    auth: false
  }, {
    title: 'Создать аккаунт',
    href: '/signup',
    auth: false
  }
]
