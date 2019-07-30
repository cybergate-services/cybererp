read -r -p "This will remove all of your persistant docker data, are you sure you want to contine? [y/N] " response
  case $response in
    [yY][eE][sS]|[yY])
      docker-compose down -v --rmi all --remove-orphans
      ;;
    *)
      exit 1
    ;;
  esac

